from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source_type: str
    base_url: str | None
    crawl_method: str
    enabled: bool
    policy_status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class SourceHealthOut(BaseModel):
    source_id: int
    source_name: str
    source_type: str
    crawl_method: str
    policy_status: str
    enabled: bool
    last_status: str | None
    last_finished_at: datetime | None
    recent_error_count: int
    success_rate: float | None
