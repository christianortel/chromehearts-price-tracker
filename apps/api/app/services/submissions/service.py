from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import AdminAuditLog, PriceObservation, RetailReport, Source, UserSubmission
from app.schemas.submissions import SubmissionCreate
from app.services.normalization import build_duplicate_group_key, normalize_text


def create_submission(db: Session, payload: SubmissionCreate) -> UserSubmission:
    submission = UserSubmission(**payload.model_dump(), status="pending")
    db.add(submission)
    db.flush()
    return submission


def review_submission(
    db: Session,
    submission_id: int,
    decision: str,
    admin_identifier: str = "token-admin",
    product_id: int | None = None,
) -> UserSubmission:
    submission = db.query(UserSubmission).filter(UserSubmission.id == submission_id).one()
    submission.status = decision
    if decision == "approved":
        source = db.query(Source).filter(Source.name == "community_submissions").one()
        normalized_title = normalize_text(submission.item_name)
        observation = PriceObservation(
            product_id=product_id,
            raw_title=submission.item_name,
            normalized_title=normalized_title,
            source_id=source.id,
            source_item_id=f"submission-{submission.id}",
            source_url=f"submission://{submission.id}",
            source_type_snapshot=source.source_type,
            market_side="retail",
            seller_or_store=submission.store,
            location_text=", ".join(filter(None, [submission.city, submission.country])) or None,
            currency=submission.currency,
            price_amount=submission.price,
            observed_at=datetime.combine(
                submission.date_seen or datetime.now(UTC).date(),
                datetime.min.time(),
                tzinfo=UTC,
            ),
            status="active",
            proof_type="receipt" if submission.receipt_asset_url else "claim",
            proof_asset_url=submission.receipt_asset_url,
            extraction_confidence=Decimal("0.950"),
            match_confidence=Decimal("0.750") if product_id else Decimal("0.000"),
            price_confidence=Decimal("0.950") if submission.receipt_asset_url else Decimal("0.700"),
            duplicate_group_key=build_duplicate_group_key(
                "community_submissions",
                normalized_title,
                f"{submission.price:.2f}",
                str(submission.date_seen or ""),
            ),
            raw_payload_json={"submission_id": submission.id},
        )
        db.add(observation)
        db.flush()
        db.add(
            RetailReport(
                source_observation_id=observation.id,
                product_id=product_id,
                store_name=submission.store,
                city=submission.city,
                country=submission.country,
                receipt_submitted=bool(submission.receipt_asset_url),
                moderator_status="approved",
            )
        )
    db.add(
        AdminAuditLog(
            admin_identifier=admin_identifier,
            action=f"submission_{decision}",
            target_type="user_submission",
            target_id=str(submission_id),
            payload_json={"product_id": product_id},
        )
    )
    db.flush()
    return submission

