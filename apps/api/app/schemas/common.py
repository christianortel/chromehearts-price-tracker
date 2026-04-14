from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MetricSnapshotOut(ApiModel):
    id: int
    product_id: int
    snapshot_date: date
    retail_low: Decimal | None
    retail_high: Decimal | None
    retail_best_known: Decimal | None
    ask_median: Decimal | None
    ask_low: Decimal | None
    ask_high: Decimal | None
    sold_median_30d: Decimal | None
    sold_median_90d: Decimal | None
    sample_size_asks: int
    sample_size_solds: int
    premium_vs_retail_pct: Decimal | None
    premium_vs_retail_abs: Decimal | None
    freshness_score: Decimal | None
    confidence_score: Decimal | None
    generated_at: datetime
