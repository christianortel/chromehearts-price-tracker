from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from statistics import median

from sqlalchemy.orm import Session

from app.models import MetricSnapshot, PriceObservation


def _decimal_median(values: list[Decimal]) -> Decimal | None:
    if not values:
        return None
    return Decimal(str(median([float(value) for value in values]))).quantize(Decimal("0.01"))


def _coerce_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _freshness_score(latest_seen_at: datetime | None) -> Decimal | None:
    latest_seen = _coerce_utc(latest_seen_at)
    if latest_seen is None:
        return None
    days_old = max((datetime.now(UTC) - latest_seen).days, 0)
    score = max(0.05, 1 - (days_old / 180))
    return Decimal(str(round(score, 3)))


def recompute_product_metrics(db: Session, product_id: int) -> MetricSnapshot:
    observations = (
        db.query(PriceObservation)
        .filter(
            PriceObservation.product_id == product_id,
            PriceObservation.status.in_(["active", "pending_review"]),
        )
        .all()
    )
    retail = [
        observation
        for observation in observations
        if observation.market_side == "retail" and observation.price_confidence >= Decimal("0.600")
    ]
    asks = [
        observation
        for observation in observations
        if observation.market_side == "ask" and observation.price_confidence >= Decimal("0.500")
    ]
    solds = [
        observation
        for observation in observations
        if observation.market_side == "sold" and observation.price_confidence >= Decimal("0.650")
    ]

    retail_prices = [observation.price_amount for observation in retail]
    ask_prices = [observation.price_amount for observation in asks]

    sold_30d = [
        observation.price_amount
        for observation in solds
        if (_coerce_utc(observation.observed_at) or datetime.min.replace(tzinfo=UTC))
        >= datetime.now(UTC) - timedelta(days=30)
    ]
    sold_90d = [
        observation.price_amount
        for observation in solds
        if (_coerce_utc(observation.observed_at) or datetime.min.replace(tzinfo=UTC))
        >= datetime.now(UTC) - timedelta(days=90)
    ]

    best_known_retail = min(retail_prices) if retail_prices else None
    ask_median = _decimal_median(ask_prices)
    latest_seen_candidates = [
        normalized_seen_at
        for observation in observations
        if (normalized_seen_at := _coerce_utc(observation.last_seen_at)) is not None
    ]
    latest_seen = max(latest_seen_candidates) if latest_seen_candidates else None
    freshness = _freshness_score(latest_seen)
    confidence_components = [
        float(observation.price_confidence) for observation in observations[:25]
    ]
    confidence = (
        Decimal(str(round(sum(confidence_components) / len(confidence_components), 3)))
        if confidence_components
        else None
    )

    premium_abs = None
    premium_pct = None
    if best_known_retail and ask_median and best_known_retail > 0:
        premium_abs = (ask_median - best_known_retail).quantize(Decimal("0.01"))
        premium_pct = ((premium_abs / best_known_retail) * Decimal("100")).quantize(
            Decimal("0.0001")
        )

    snapshot = (
        db.query(MetricSnapshot)
        .filter(
            MetricSnapshot.product_id == product_id, MetricSnapshot.snapshot_date == date.today()
        )
        .one_or_none()
    )
    if snapshot is None:
        snapshot = MetricSnapshot(product_id=product_id, snapshot_date=date.today())
        db.add(snapshot)

    snapshot.retail_low = min(retail_prices) if retail_prices else None
    snapshot.retail_high = max(retail_prices) if retail_prices else None
    snapshot.retail_best_known = best_known_retail
    snapshot.ask_median = ask_median
    snapshot.ask_low = min(ask_prices) if ask_prices else None
    snapshot.ask_high = max(ask_prices) if ask_prices else None
    snapshot.sold_median_30d = _decimal_median(sold_30d)
    snapshot.sold_median_90d = _decimal_median(sold_90d)
    snapshot.sample_size_asks = len(ask_prices)
    snapshot.sample_size_solds = len(sold_90d)
    snapshot.premium_vs_retail_abs = premium_abs
    snapshot.premium_vs_retail_pct = premium_pct
    snapshot.freshness_score = freshness
    snapshot.confidence_score = confidence
    snapshot.generated_at = datetime.now(UTC)
    db.flush()
    return snapshot
