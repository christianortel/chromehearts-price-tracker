from datetime import UTC, datetime

from app.core.security import require_admin
from app.db.session import get_db
from app.models import (
    AdminAuditLog,
    ItemMatchReview,
    PriceObservation,
    Product,
    ProductAlias,
    RetailReport,
    ScrapeError,
    ScrapeRun,
    Source,
    UserSubmission,
)
from app.schemas.admin import (
    AdminAssetPreviewOut,
    AdminObservationDetailOut,
    AdminObservationMatchReviewOut,
    AdminObservationRetailReportOut,
    AdminProductSearchResponse,
    AdminSubmissionOut,
    DuplicateObservationGroupOut,
    DuplicateObservationOut,
    DuplicateResolveOut,
    DuplicateResolveRequest,
    DuplicateReviewRequest,
    MatchCandidateOut,
    MatchRequest,
    ProductAliasCreate,
    ProductAliasOut,
    RecomputeRequest,
    ScrapeErrorOut,
    ScrapeRunDetailOut,
    ScrapeRunOut,
    SourceRunRequest,
    SourceToggleRequest,
    UnmatchedObservationOut,
)
from app.schemas.common import MetricSnapshotOut
from app.schemas.products import ObservationOut
from app.schemas.sources import SourceHealthOut, SourceOut
from app.services.artifacts import build_asset_preview
from app.services.catalog_search import search_catalog_products
from app.services.matching.engine import (
    MatchCandidate,
    build_match_catalog,
    rank_products,
    rank_products_against_catalog,
)
from app.services.metrics.engine import recompute_product_metrics
from app.services.operations.duplicates import (
    apply_duplicate_decision,
    recommend_duplicate_keeper,
    resolve_duplicate_group,
)
from app.services.operations.source_runs import execute_source_run, set_source_enabled
from app.services.submissions.service import review_submission
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def serialize_match_candidate(candidate: MatchCandidate) -> MatchCandidateOut:
    return MatchCandidateOut(
        product_id=candidate.product_id,
        product_name=getattr(candidate, "product_name", None),
        score=float(candidate.score),
        reason=candidate.reason,
    )


def serialize_scrape_run(run: ScrapeRun, source_name: str | None) -> ScrapeRunOut:
    return ScrapeRunOut(
        id=run.id,
        source_id=run.source_id,
        source_name=source_name,
        started_at=run.started_at,
        finished_at=run.finished_at,
        status=run.status,
        discovered_count=run.discovered_count,
        parsed_count=run.parsed_count,
        inserted_count=run.inserted_count,
        error_count=run.error_count,
        notes=run.notes,
    )


def serialize_scrape_error(error: ScrapeError, source_name: str | None) -> ScrapeErrorOut:
    return ScrapeErrorOut(
        id=error.id,
        scrape_run_id=error.scrape_run_id,
        source_id=error.source_id,
        source_name=source_name,
        item_reference=error.item_reference,
        error_type=error.error_type,
        error_message=error.error_message,
        html_snapshot_path=error.html_snapshot_path,
        screenshot_path=error.screenshot_path,
        created_at=error.created_at,
    )


def serialize_match_review(
    review: ItemMatchReview, proposed_product_name: str | None
) -> AdminObservationMatchReviewOut:
    return AdminObservationMatchReviewOut(
        id=review.id,
        proposed_product_id=review.proposed_product_id,
        proposed_product_name=proposed_product_name,
        reviewer_decision=review.reviewer_decision,
        reviewer_notes=review.reviewer_notes,
        reviewed_at=review.reviewed_at,
    )


def serialize_retail_report(report: RetailReport) -> AdminObservationRetailReportOut:
    return AdminObservationRetailReportOut(
        id=report.id,
        store_name=report.store_name,
        city=report.city,
        country=report.country,
        receipt_submitted=report.receipt_submitted,
        moderator_status=report.moderator_status,
        moderator_notes=report.moderator_notes,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def serialize_duplicate_observation(
    observation: PriceObservation,
    source_name: str | None,
    product_name: str | None,
) -> DuplicateObservationOut:
    return DuplicateObservationOut(
        **observation.__dict__,
        source_name=source_name or f"source-{observation.source_id}",
        product_name=product_name,
    )


@router.get("/unmatched", response_model=list[UnmatchedObservationOut])
def get_unmatched(db: Session = Depends(get_db)) -> list[UnmatchedObservationOut]:
    catalog = build_match_catalog(db)
    observations = (
        db.query(PriceObservation, Source.name.label("source_name"))
        .join(Source, Source.id == PriceObservation.source_id)
        .filter(
            (PriceObservation.product_id.is_(None)) | (PriceObservation.match_confidence < 0.7),
            PriceObservation.status != "rejected",
        )
        .order_by(PriceObservation.observed_at.desc())
        .limit(200)
        .all()
    )
    return [
        UnmatchedObservationOut(
            **observation.__dict__,
            source_name=source_name,
            top_candidates=[
                serialize_match_candidate(candidate)
                for candidate in rank_products_against_catalog(observation.raw_title, catalog)[:5]
            ],
        )
        for observation, source_name in observations
    ]


@router.get("/products/search", response_model=AdminProductSearchResponse)
def admin_product_search(
    q: str = Query(min_length=1),
    limit: int = Query(default=15, le=50),
    db: Session = Depends(get_db),
) -> AdminProductSearchResponse:
    items = search_catalog_products(db, q, limit=limit)
    return AdminProductSearchResponse(query=q, total=len(items), items=items)


@router.get("/observations/{observation_id}", response_model=AdminObservationDetailOut)
def admin_observation_detail(
    observation_id: int, db: Session = Depends(get_db)
) -> AdminObservationDetailOut:
    observation = (
        db.query(PriceObservation).filter(PriceObservation.id == observation_id).one_or_none()
    )
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")

    review_product_ids = [
        review.proposed_product_id
        for review in observation.match_reviews
        if review.proposed_product_id is not None
    ]
    proposed_products = (
        {
            product.id: product.canonical_name
            for product in db.query(Product).filter(Product.id.in_(review_product_ids)).all()
        }
        if review_product_ids
        else {}
    )
    observation_payload = ObservationOut.model_validate(observation).model_dump()

    return AdminObservationDetailOut(
        **observation_payload,
        first_seen_at=observation.first_seen_at,
        created_at=observation.created_at,
        updated_at=observation.updated_at,
        source_name=observation.source.name
        if observation.source
        else f"source-{observation.source_id}",
        product_name=observation.product.canonical_name if observation.product else None,
        variant_key=observation.variant.variant_key if observation.variant else None,
        duplicate_group_key=observation.duplicate_group_key,
        top_candidates=[
            serialize_match_candidate(candidate)
            for candidate in rank_products(db, observation.raw_title)[:5]
        ],
        retail_report=serialize_retail_report(observation.retail_report)
        if observation.retail_report
        else None,
        match_reviews=[
            serialize_match_review(
                review,
                proposed_products.get(review.proposed_product_id)
                if review.proposed_product_id is not None
                else None,
            )
            for review in sorted(
                observation.match_reviews,
                key=lambda item: item.reviewed_at or datetime.min.replace(tzinfo=UTC),
                reverse=True,
            )
        ],
    )


@router.post("/match")
def post_match(payload: MatchRequest, db: Session = Depends(get_db)) -> dict:
    observation = (
        db.query(PriceObservation)
        .filter(PriceObservation.id == payload.observation_id)
        .one_or_none()
    )
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    if payload.product_id is None and payload.decision == "matched":
        ranking = rank_products(db, observation.raw_title)
        if ranking:
            payload.product_id = ranking[0].product_id
            observation.match_confidence = ranking[0].score
    observation.product_id = payload.product_id
    observation.status = "active" if payload.product_id else "pending_review"
    db.add(
        ItemMatchReview(
            observation_id=observation.id,
            proposed_product_id=payload.product_id,
            reviewer_decision=payload.decision,
            reviewer_notes=payload.reviewer_notes,
            reviewed_at=datetime.now(UTC),
        )
    )
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="observation_match_review",
            target_type="price_observation",
            target_id=str(observation.id),
            payload_json=payload.model_dump(),
        )
    )
    db.commit()
    return {"status": "ok", "observation_id": observation.id, "product_id": observation.product_id}


@router.get("/observations/{observation_id}/candidates", response_model=list[MatchCandidateOut])
def get_observation_candidates(
    observation_id: int, db: Session = Depends(get_db)
) -> list[MatchCandidateOut]:
    observation = (
        db.query(PriceObservation).filter(PriceObservation.id == observation_id).one_or_none()
    )
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    return [
        serialize_match_candidate(candidate)
        for candidate in rank_products(db, observation.raw_title)[:10]
    ]


@router.post("/recompute", response_model=list[MetricSnapshotOut])
def recompute(payload: RecomputeRequest, db: Session = Depends(get_db)) -> list[MetricSnapshotOut]:
    product_ids = (
        [payload.product_id]
        if payload.product_id
        else [product.id for product in db.query(Product.id).all()]
    )
    snapshots = [
        recompute_product_metrics(db, product_id)
        for product_id in product_ids
        if product_id is not None
    ]
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="metrics_recompute",
            target_type="product",
            target_id=str(payload.product_id) if payload.product_id else None,
            payload_json={"count": len(snapshots)},
        )
    )
    db.commit()
    return [MetricSnapshotOut.model_validate(snapshot) for snapshot in snapshots]


@router.get("/scrape-runs", response_model=list[ScrapeRunOut])
def admin_scrape_runs(
    limit: int = Query(default=50, le=200), db: Session = Depends(get_db)
) -> list[ScrapeRunOut]:
    runs = (
        db.query(ScrapeRun, Source.name.label("source_name"))
        .join(Source, Source.id == ScrapeRun.source_id)
        .order_by(ScrapeRun.started_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_scrape_run(run, source_name) for run, source_name in runs]


@router.get("/duplicates", response_model=list[DuplicateObservationGroupOut])
def admin_duplicate_groups(
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
) -> list[DuplicateObservationGroupOut]:
    groups = (
        db.query(
            PriceObservation.duplicate_group_key.label("duplicate_group_key"),
            func.count(PriceObservation.id).label("duplicate_count"),
            func.max(PriceObservation.observed_at).label("latest_observed_at"),
        )
        .filter(
            PriceObservation.duplicate_group_key.is_not(None),
            PriceObservation.status.in_(["active", "pending_review"]),
        )
        .group_by(PriceObservation.duplicate_group_key)
        .having(func.count(PriceObservation.id) > 1)
        .order_by(func.max(PriceObservation.observed_at).desc())
        .limit(limit)
        .all()
    )
    payload: list[DuplicateObservationGroupOut] = []
    for group in groups:
        group_rows = (
            db.query(
                PriceObservation,
                Source.name.label("source_name"),
                Product.canonical_name.label("product_name"),
            )
            .join(Source, Source.id == PriceObservation.source_id)
            .outerjoin(Product, Product.id == PriceObservation.product_id)
            .filter(
                PriceObservation.duplicate_group_key == group.duplicate_group_key,
                PriceObservation.status.in_(["active", "pending_review"]),
            )
            .order_by(PriceObservation.observed_at.desc(), PriceObservation.id.desc())
            .all()
        )
        recommendation = recommend_duplicate_keeper(
            [observation for observation, _, _ in group_rows]
        )
        payload.append(
            DuplicateObservationGroupOut(
                duplicate_group_key=group.duplicate_group_key,
                duplicate_count=int(group.duplicate_count),
                latest_observed_at=group.latest_observed_at,
                suggested_keep_observation_id=recommendation.observation_id
                if recommendation
                else None,
                suggested_keep_reason=recommendation.reason if recommendation else None,
                observations=[
                    serialize_duplicate_observation(observation, source_name, product_name)
                    for observation, source_name, product_name in group_rows
                ],
            )
        )
    return payload


@router.get("/scrape-runs/{run_id}", response_model=ScrapeRunDetailOut)
def admin_scrape_run_detail(run_id: int, db: Session = Depends(get_db)) -> ScrapeRunDetailOut:
    row = (
        db.query(ScrapeRun, Source.name.label("source_name"))
        .join(Source, Source.id == ScrapeRun.source_id)
        .filter(ScrapeRun.id == run_id)
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Scrape run not found")
    run, source_name = row
    errors = (
        db.query(ScrapeError, Source.name.label("source_name"))
        .join(Source, Source.id == ScrapeError.source_id)
        .filter(ScrapeError.scrape_run_id == run_id)
        .order_by(ScrapeError.created_at.desc())
        .all()
    )
    return ScrapeRunDetailOut(
        **serialize_scrape_run(run, source_name).model_dump(),
        errors=[
            serialize_scrape_error(error, error_source_name) for error, error_source_name in errors
        ],
    )


@router.get("/assets/preview", response_model=AdminAssetPreviewOut)
def admin_asset_preview(
    path: str = Query(min_length=1), db: Session = Depends(get_db)
) -> AdminAssetPreviewOut:
    del db
    try:
        preview = build_asset_preview(path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AdminAssetPreviewOut(**preview.__dict__)


@router.post("/duplicates/review")
def review_duplicate(payload: DuplicateReviewRequest, db: Session = Depends(get_db)) -> dict:
    observation = (
        db.query(PriceObservation)
        .filter(PriceObservation.id == payload.observation_id)
        .one_or_none()
    )
    if observation is None:
        raise HTTPException(status_code=404, detail="Observation not found")
    if observation.duplicate_group_key is None:
        raise HTTPException(status_code=400, detail="Observation has no duplicate group key")

    apply_duplicate_decision(observation, payload.decision, reviewer_notes=payload.reviewer_notes)

    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="duplicate_review",
            target_type="price_observation",
            target_id=str(observation.id),
            payload_json=payload.model_dump(),
        )
    )
    db.commit()
    return {"status": "ok", "observation_id": observation.id, "decision": payload.decision}


@router.post("/duplicates/resolve", response_model=DuplicateResolveOut)
def resolve_duplicates(
    payload: DuplicateResolveRequest, db: Session = Depends(get_db)
) -> DuplicateResolveOut:
    try:
        result = resolve_duplicate_group(
            db,
            duplicate_group_key=payload.duplicate_group_key,
            keep_observation_id=payload.keep_observation_id,
            reviewer_notes=payload.reviewer_notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.commit()
    return DuplicateResolveOut(
        status="ok",
        duplicate_group_key=result.duplicate_group_key,
        keep_observation_id=result.keep_observation_id,
        rejected_observation_ids=result.rejected_observation_ids,
    )


@router.get("/source-health", response_model=list[SourceHealthOut])
def admin_source_health(db: Session = Depends(get_db)) -> list[SourceHealthOut]:
    latest_run_by_source = (
        db.query(
            Source.id.label("source_id"),
            Source.name.label("source_name"),
            Source.source_type.label("source_type"),
            Source.crawl_method.label("crawl_method"),
            Source.policy_status.label("policy_status"),
            Source.enabled.label("enabled"),
            func.max(ScrapeRun.finished_at).label("last_finished_at"),
        )
        .outerjoin(ScrapeRun, ScrapeRun.source_id == Source.id)
        .group_by(
            Source.id,
            Source.name,
            Source.source_type,
            Source.crawl_method,
            Source.policy_status,
            Source.enabled,
        )
        .all()
    )
    results: list[SourceHealthOut] = []
    for row in latest_run_by_source:
        recent_runs = (
            db.query(ScrapeRun)
            .filter(ScrapeRun.source_id == row.source_id)
            .order_by(ScrapeRun.started_at.desc())
            .limit(10)
            .all()
        )
        success_rate = None
        if recent_runs:
            success_rate = round(
                sum(1 for run in recent_runs if run.status == "success") / len(recent_runs), 3
            )
        recent_error_count = sum(run.error_count for run in recent_runs)
        last_status = recent_runs[0].status if recent_runs else None
        results.append(
            SourceHealthOut(
                source_id=row.source_id,
                source_name=row.source_name,
                source_type=row.source_type,
                crawl_method=row.crawl_method,
                policy_status=row.policy_status,
                enabled=row.enabled,
                last_status=last_status,
                last_finished_at=row.last_finished_at,
                recent_error_count=recent_error_count,
                success_rate=success_rate,
            )
        )
    return results


@router.post("/sources/{source_id}/run", response_model=ScrapeRunOut)
def run_source(
    source_id: int, payload: SourceRunRequest, db: Session = Depends(get_db)
) -> ScrapeRunOut:
    source = db.query(Source).filter(Source.id == source_id).one_or_none()
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    result = execute_source_run(
        db, source.name, query=payload.query, html_override=payload.html_override
    )
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="source_run_trigger",
            target_type="source",
            target_id=str(source_id),
            payload_json={"query": payload.query, "status": result.run.status},
        )
    )
    db.commit()
    db.refresh(result.run)
    return serialize_scrape_run(result.run, source.name)


@router.post("/sources/{source_id}/toggle", response_model=SourceOut)
def toggle_source(
    source_id: int, payload: SourceToggleRequest, db: Session = Depends(get_db)
) -> SourceOut:
    try:
        source = set_source_enabled(db, source_id, payload.enabled)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="source_toggle",
            target_type="source",
            target_id=str(source_id),
            payload_json={"enabled": payload.enabled},
        )
    )
    db.commit()
    db.refresh(source)
    return SourceOut.model_validate(source)


@router.get("/submissions", response_model=list[AdminSubmissionOut])
def admin_submissions(
    status: str | None = Query(default=None), db: Session = Depends(get_db)
) -> list[AdminSubmissionOut]:
    query = db.query(UserSubmission)
    if status:
        query = query.filter(UserSubmission.status == status)
    submissions = query.order_by(UserSubmission.created_at.desc()).limit(200).all()
    return [
        AdminSubmissionOut(
            **AdminSubmissionOut.model_validate(submission).model_dump(exclude={"top_candidates"}),
            top_candidates=[
                serialize_match_candidate(candidate)
                for candidate in rank_products(db, submission.item_name)[:5]
            ],
        )
        for submission in submissions
    ]


@router.post("/submissions/{submission_id}/decision", response_model=AdminSubmissionOut)
def admin_review_submission(
    submission_id: int,
    decision: str = Query(pattern="^(approved|rejected)$"),
    product_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
) -> AdminSubmissionOut:
    submission = review_submission(db, submission_id, decision=decision, product_id=product_id)
    db.commit()
    db.refresh(submission)
    return AdminSubmissionOut.model_validate(submission)


@router.get("/products/{product_id}/aliases", response_model=list[ProductAliasOut])
def get_product_aliases(product_id: int, db: Session = Depends(get_db)) -> list[ProductAliasOut]:
    product = db.query(Product).filter(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    aliases = (
        db.query(ProductAlias)
        .filter(ProductAlias.product_id == product_id)
        .order_by(ProductAlias.alias_text.asc())
        .all()
    )
    return [ProductAliasOut.model_validate(alias) for alias in aliases]


@router.post("/products/{product_id}/aliases", response_model=ProductAliasOut)
def create_product_alias(
    product_id: int, payload: ProductAliasCreate, db: Session = Depends(get_db)
) -> ProductAliasOut:
    product = db.query(Product).filter(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    alias = (
        db.query(ProductAlias)
        .filter(
            ProductAlias.product_id == product_id,
            func.lower(ProductAlias.alias_text) == payload.alias_text.lower(),
        )
        .one_or_none()
    )
    if alias is not None:
        raise HTTPException(status_code=409, detail="Alias already exists for this product")
    alias = ProductAlias(product_id=product_id, **payload.model_dump())
    db.add(alias)
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="alias_create",
            target_type="product_alias",
            target_id=None,
            payload_json={"product_id": product_id, **payload.model_dump()},
        )
    )
    db.commit()
    db.refresh(alias)
    return ProductAliasOut.model_validate(alias)


@router.delete("/aliases/{alias_id}")
def delete_product_alias(alias_id: int, db: Session = Depends(get_db)) -> dict:
    alias = db.query(ProductAlias).filter(ProductAlias.id == alias_id).one_or_none()
    if alias is None:
        raise HTTPException(status_code=404, detail="Alias not found")
    db.add(
        AdminAuditLog(
            admin_identifier="token-admin",
            action="alias_delete",
            target_type="product_alias",
            target_id=str(alias_id),
            payload_json={"product_id": alias.product_id, "alias_text": alias.alias_text},
        )
    )
    db.delete(alias)
    db.commit()
    return {"status": "ok", "alias_id": alias_id}
