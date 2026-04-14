from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    submission_type: str = Field(default="retail_report")
    item_name: str = Field(min_length=2, max_length=255)
    price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    store: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=128)
    country: str | None = Field(default=None, max_length=128)
    date_seen: date | None = None
    notes: str | None = Field(default=None, max_length=4000)
    receipt_asset_url: str | None = Field(default=None, max_length=1024)


class SubmissionAssetUploadOut(BaseModel):
    asset_path: str
    content_type: str
    file_name: str
    byte_size: int


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_type: str
    item_name: str
    price: Decimal
    currency: str
    store: str | None
    city: str | None
    country: str | None
    date_seen: date | None
    notes: str | None
    receipt_asset_url: str | None
    status: str
    created_at: datetime
