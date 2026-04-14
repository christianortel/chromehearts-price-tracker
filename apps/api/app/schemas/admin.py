from datetime import datetime

from app.schemas.products import ObservationOut, ProductListItem
from app.schemas.submissions import SubmissionOut
from pydantic import BaseModel, ConfigDict, Field


class MatchCandidateOut(BaseModel):
    product_id: int
    product_name: str | None = None
    score: float
    reason: str


class AdminObservationMatchReviewOut(BaseModel):
    id: int
    proposed_product_id: int | None = None
    proposed_product_name: str | None = None
    reviewer_decision: str
    reviewer_notes: str | None = None
    reviewed_at: datetime | None = None


class AdminObservationRetailReportOut(BaseModel):
    id: int
    store_name: str | None = None
    city: str | None = None
    country: str | None = None
    receipt_submitted: bool
    moderator_status: str
    moderator_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class MatchRequest(BaseModel):
    observation_id: int
    product_id: int | None = None
    reviewer_notes: str | None = Field(default=None, max_length=2000)
    decision: str = "matched"


class RecomputeRequest(BaseModel):
    product_id: int | None = None


class SourceRunRequest(BaseModel):
    query: str = Field(default="chrome hearts", min_length=2, max_length=255)
    html_override: str | None = Field(
        default=None,
        max_length=500_000,
        description="Admin-only fixture/debug override used for parser validation and tests.",
    )


class SourceToggleRequest(BaseModel):
    enabled: bool


class DuplicateReviewRequest(BaseModel):
    observation_id: int
    decision: str = Field(pattern="^(reject|restore)$")
    reviewer_notes: str | None = Field(default=None, max_length=2000)


class DuplicateResolveRequest(BaseModel):
    duplicate_group_key: str = Field(min_length=8, max_length=255)
    keep_observation_id: int
    reviewer_notes: str | None = Field(default=None, max_length=2000)


class DuplicateResolveOut(BaseModel):
    status: str
    duplicate_group_key: str
    keep_observation_id: int
    rejected_observation_ids: list[int] = Field(default_factory=list)


class ScrapeRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    source_name: str | None = None
    started_at: datetime
    finished_at: datetime | None
    status: str
    discovered_count: int
    parsed_count: int
    inserted_count: int
    error_count: int
    notes: str | None


class ScrapeErrorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scrape_run_id: int
    source_id: int
    source_name: str | None = None
    item_reference: str | None
    error_type: str
    error_message: str
    html_snapshot_path: str | None
    screenshot_path: str | None
    created_at: datetime


class ScrapeRunDetailOut(ScrapeRunOut):
    errors: list[ScrapeErrorOut] = Field(default_factory=list)


class AdminAssetPreviewOut(BaseModel):
    asset_path: str
    content_type: str
    kind: str
    file_name: str
    byte_size: int
    truncated: bool
    text_content: str | None = None
    base64_content: str | None = None


class UnmatchedObservationOut(ObservationOut):
    source_name: str
    top_candidates: list[MatchCandidateOut] = Field(default_factory=list)


class AdminObservationDetailOut(ObservationOut):
    source_name: str
    product_name: str | None = None
    variant_key: str | None = None
    duplicate_group_key: str | None = None
    first_seen_at: datetime
    created_at: datetime
    updated_at: datetime
    top_candidates: list[MatchCandidateOut] = Field(default_factory=list)
    retail_report: AdminObservationRetailReportOut | None = None
    match_reviews: list[AdminObservationMatchReviewOut] = Field(default_factory=list)


class AdminProductSearchResponse(BaseModel):
    query: str
    total: int
    items: list[ProductListItem]


class DuplicateObservationOut(ObservationOut):
    source_name: str
    product_name: str | None = None


class DuplicateObservationGroupOut(BaseModel):
    duplicate_group_key: str
    duplicate_count: int
    latest_observed_at: datetime
    suggested_keep_observation_id: int | None = None
    suggested_keep_reason: str | None = None
    observations: list[DuplicateObservationOut] = Field(default_factory=list)


class AdminSubmissionOut(SubmissionOut):
    top_candidates: list[MatchCandidateOut] = Field(default_factory=list)


class ProductAliasOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    alias_text: str
    alias_type: str
    source_name: str | None
    created_at: datetime


class ProductAliasCreate(BaseModel):
    alias_text: str = Field(min_length=2, max_length=255)
    alias_type: str = Field(default="manual", max_length=64)
    source_name: str | None = Field(default="admin")
