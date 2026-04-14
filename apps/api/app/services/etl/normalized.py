from datetime import UTC, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class NormalizedObservation(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source_name: str
    source_type: str
    source_item_id: str
    source_url: str
    raw_title: str
    normalized_title: str
    market_side: str
    seller_or_store: str | None = None
    location_text: str | None = None
    condition: str | None = None
    size_text: str | None = None
    currency: str = "USD"
    price_amount: Decimal
    shipping_amount: Decimal | None = None
    tax_included: bool | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: str = "pending_review"
    proof_type: str | None = None
    proof_asset_url: str | None = None
    raw_payload: dict
    extraction_confidence: Decimal = Decimal("0.500")
    match_confidence: Decimal = Decimal("0.000")
    price_confidence: Decimal = Decimal("0.500")
    duplicate_group_key: str | None = None
