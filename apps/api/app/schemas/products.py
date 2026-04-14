from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.common import MetricSnapshotOut


class ProductListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_name: str
    slug: str
    category: str
    subcategory: str | None
    material: str | None
    updated_at: datetime
    latest_metric: MetricSnapshotOut | None = None


class ProductFacetCount(BaseModel):
    key: str
    label: str
    count: int


class ProductBrowseFacets(BaseModel):
    categories: list[ProductFacetCount]
    source_types: list[ProductFacetCount]
    market_sides: list[ProductFacetCount]


class ProductBrowseResponse(BaseModel):
    total: int
    limit: int
    offset: int
    has_next_page: bool
    items: list[ProductListItem]
    facets: ProductBrowseFacets


class ObservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int | None
    raw_title: str
    normalized_title: str
    source_id: int
    source_item_id: str
    source_url: str
    source_type_snapshot: str
    market_side: str
    seller_or_store: str | None
    location_text: str | None
    condition: str | None
    size_text: str | None
    currency: str
    price_amount: Decimal
    shipping_amount: Decimal | None
    tax_included: bool | None
    observed_at: datetime
    last_seen_at: datetime
    status: str
    proof_type: str | None
    proof_asset_url: str | None
    extraction_confidence: Decimal
    match_confidence: Decimal
    price_confidence: Decimal
    raw_payload_json: dict


class ProductDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    canonical_name: str
    slug: str
    category: str
    subcategory: str | None
    material: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    latest_metric: MetricSnapshotOut | None = None
    observations: list[ObservationOut] = []
    aliases: list[str] = []
