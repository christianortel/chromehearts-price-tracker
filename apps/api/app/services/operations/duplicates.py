from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import AdminAuditLog, PriceObservation

SOURCE_TYPE_WEIGHTS = {
    "community_retail": Decimal("1.50"),
    "curated_reseller": Decimal("1.10"),
    "sold_comp": Decimal("1.25"),
    "import": Decimal("0.90"),
    "marketplace": Decimal("0.70"),
}

PROOF_TYPE_WEIGHTS = {
    "receipt": Decimal("2.50"),
    "listing": Decimal("1.25"),
    "claim": Decimal("0.50"),
}


@dataclass(slots=True)
class DuplicateKeeperRecommendation:
    observation_id: int
    reason: str


@dataclass(slots=True)
class DuplicateResolutionResult:
    duplicate_group_key: str
    keep_observation_id: int
    rejected_observation_ids: list[int]


def _restore_status(observation: PriceObservation) -> str:
    return "active" if observation.product_id else "pending_review"


def _sync_retail_report(
    observation: PriceObservation, moderator_status: str, reviewer_notes: str | None
) -> None:
    if observation.retail_report is None:
        return
    observation.retail_report.moderator_status = moderator_status
    if reviewer_notes:
        observation.retail_report.moderator_notes = reviewer_notes


def apply_duplicate_decision(
    observation: PriceObservation,
    decision: str,
    reviewer_notes: str | None = None,
) -> None:
    if decision == "reject":
        observation.status = "rejected"
        _sync_retail_report(
            observation,
            moderator_status="rejected",
            reviewer_notes=reviewer_notes or "Rejected during duplicate review.",
        )
        return

    if decision != "restore":
        raise ValueError(f"Unsupported duplicate decision: {decision}")

    observation.status = _restore_status(observation)
    _sync_retail_report(
        observation,
        moderator_status="approved",
        reviewer_notes=reviewer_notes or "Restored during duplicate review.",
    )


def _score_observation(observation: PriceObservation) -> Decimal:
    score = Decimal("0.000")
    score += PROOF_TYPE_WEIGHTS.get(observation.proof_type or "", Decimal("0.000"))
    score += SOURCE_TYPE_WEIGHTS.get(observation.source_type_snapshot, Decimal("0.000"))
    score += observation.price_confidence * Decimal("2.000")
    score += observation.extraction_confidence
    score += observation.match_confidence
    if observation.product_id is not None:
        score += Decimal("0.750")
    if observation.proof_asset_url:
        score += Decimal("0.500")
    if observation.status == "active":
        score += Decimal("0.100")
    score += Decimal(str(observation.observed_at.timestamp())) / Decimal("1000000000000")
    return score


def _build_recommendation_reason(observation: PriceObservation) -> str:
    reasons: list[str] = []
    if observation.proof_type == "receipt" or observation.proof_asset_url:
        reasons.append("receipt-backed evidence")
    elif observation.proof_type == "listing":
        reasons.append("listing-backed evidence")
    elif observation.proof_type:
        reasons.append(f"{observation.proof_type}-backed evidence")

    if observation.product_id is not None:
        reasons.append("already matched to a canonical product")

    source_reason = {
        "community_retail": "community retail source",
        "curated_reseller": "curated reseller source",
        "marketplace": "marketplace listing",
        "sold_comp": "sold-comp source",
        "import": "imported legacy evidence",
    }.get(observation.source_type_snapshot)
    if source_reason:
        reasons.append(source_reason)

    if observation.price_confidence >= Decimal("0.900"):
        reasons.append("strong price confidence")
    elif observation.match_confidence >= Decimal("0.850"):
        reasons.append("strong match confidence")

    return (
        ", ".join(reasons[:3])
        if reasons
        else "best overall evidence quality in this duplicate group"
    )


def recommend_duplicate_keeper(
    observations: Sequence[PriceObservation],
) -> DuplicateKeeperRecommendation | None:
    if not observations:
        return None
    ranked = sorted(
        observations,
        key=lambda observation: (_score_observation(observation), observation.id),
        reverse=True,
    )
    winner = ranked[0]
    return DuplicateKeeperRecommendation(
        observation_id=winner.id,
        reason=_build_recommendation_reason(winner),
    )


def resolve_duplicate_group(
    db: Session,
    duplicate_group_key: str,
    keep_observation_id: int,
    reviewer_notes: str | None = None,
    admin_identifier: str = "token-admin",
) -> DuplicateResolutionResult:
    observations = (
        db.query(PriceObservation)
        .filter(
            PriceObservation.duplicate_group_key == duplicate_group_key,
            PriceObservation.status != "deleted",
        )
        .order_by(PriceObservation.observed_at.desc(), PriceObservation.id.desc())
        .all()
    )
    if not observations:
        raise ValueError("Duplicate group not found")

    keep_observation = next(
        (observation for observation in observations if observation.id == keep_observation_id), None
    )
    if keep_observation is None:
        raise ValueError("Keep observation does not belong to this duplicate group")

    rejected_ids: list[int] = []
    for observation in observations:
        if observation.id == keep_observation_id:
            apply_duplicate_decision(
                observation,
                decision="restore",
                reviewer_notes=reviewer_notes
                or "Kept as the chosen observation for this duplicate group.",
            )
            continue

        apply_duplicate_decision(
            observation,
            decision="reject",
            reviewer_notes=reviewer_notes
            or f"Rejected because observation {keep_observation_id} was chosen as keeper.",
        )
        rejected_ids.append(observation.id)

    db.add(
        AdminAuditLog(
            admin_identifier=admin_identifier,
            action="duplicate_group_resolve",
            target_type="duplicate_group",
            target_id=duplicate_group_key,
            payload_json={
                "keep_observation_id": keep_observation_id,
                "rejected_observation_ids": rejected_ids,
                "reviewer_notes": reviewer_notes,
            },
        )
    )
    db.flush()
    return DuplicateResolutionResult(
        duplicate_group_key=duplicate_group_key,
        keep_observation_id=keep_observation_id,
        rejected_observation_ids=rejected_ids,
    )
