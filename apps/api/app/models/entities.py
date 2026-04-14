from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Category(StrEnum):
    TRUCKER_HAT = "trucker_hat"
    HOODIE = "hoodie"
    ZIP_UP = "zip_up"
    LONG_SLEEVE = "long_sleeve"
    RING = "ring"
    BRACELET = "bracelet"


class SourceType(StrEnum):
    COMMUNITY_RETAIL = "community_retail"
    CURATED_RESELLER = "curated_reseller"
    MARKETPLACE = "marketplace"
    SOLD_COMP = "sold_comp"
    IMPORT = "import"


class CrawlMethod(StrEnum):
    MANUAL_IMPORT = "manual_import"
    API = "api"
    STATIC_HTML = "static_html"
    BROWSER = "browser"
    MANUAL_ENTRY = "manual_entry"


class MarketSide(StrEnum):
    RETAIL = "retail"
    ASK = "ask"
    SOLD = "sold"


class ObservationStatus(StrEnum):
    ACTIVE = "active"
    STALE = "stale"
    DELETED = "deleted"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class ModeratorStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewDecision(StrEnum):
    MATCHED = "matched"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(128))
    material: Mapped[str | None] = mapped_column(String(128))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    aliases: Mapped[list[ProductAlias]] = relationship(back_populates="product", cascade="all, delete-orphan")
    variants: Mapped[list[ProductVariant]] = relationship(back_populates="product", cascade="all, delete-orphan")
    observations: Mapped[list[PriceObservation]] = relationship(back_populates="product")
    metrics: Mapped[list[MetricSnapshot]] = relationship(back_populates="product")


class ProductAlias(Base):
    __tablename__ = "product_aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    alias_text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    alias_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    product: Mapped[Product] = relationship(back_populates="aliases")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    size: Mapped[str | None] = mapped_column(String(64))
    color: Mapped[str | None] = mapped_column(String(64))
    finish: Mapped[str | None] = mapped_column(String(64))
    material_detail: Mapped[str | None] = mapped_column(String(128))
    variant_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    product: Mapped[Product] = relationship(back_populates="variants")
    observations: Mapped[list[PriceObservation]] = relationship(back_populates="variant")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(512))
    crawl_method: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    policy_status: Mapped[str] = mapped_column(String(64), default="planned", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    observations: Mapped[list[PriceObservation]] = relationship(back_populates="source")
    scrape_runs: Mapped[list[ScrapeRun]] = relationship(back_populates="source")


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), index=True)
    variant_id: Mapped[int | None] = mapped_column(ForeignKey("product_variants.id"), index=True)
    raw_title: Mapped[str] = mapped_column(String(512), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    source_item_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_type_snapshot: Mapped[str] = mapped_column(String(64), nullable=False)
    market_side: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    seller_or_store: Mapped[str | None] = mapped_column(String(255))
    location_text: Mapped[str | None] = mapped_column(String(255))
    condition: Mapped[str | None] = mapped_column(String(128))
    size_text: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    shipping_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    tax_included: Mapped[bool | None] = mapped_column(Boolean)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=ObservationStatus.PENDING_REVIEW)
    proof_type: Mapped[str | None] = mapped_column(String(64))
    proof_asset_url: Mapped[str | None] = mapped_column(String(1024))
    extraction_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.500"), nullable=False)
    match_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.000"), nullable=False)
    price_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.500"), nullable=False)
    duplicate_group_key: Mapped[str | None] = mapped_column(String(255), index=True)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    product: Mapped[Product | None] = relationship(back_populates="observations")
    variant: Mapped[ProductVariant | None] = relationship(back_populates="observations")
    source: Mapped[Source] = relationship(back_populates="observations")
    retail_report: Mapped[RetailReport | None] = relationship(back_populates="observation", uselist=False)
    match_reviews: Mapped[list[ItemMatchReview]] = relationship(back_populates="observation")


class RetailReport(Base):
    __tablename__ = "retail_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_observation_id: Mapped[int] = mapped_column(
        ForeignKey("price_observations.id"), nullable=False, unique=True
    )
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), index=True)
    store_name: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(128))
    receipt_submitted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    moderator_status: Mapped[str] = mapped_column(String(32), default=ModeratorStatus.PENDING, nullable=False)
    moderator_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    observation: Mapped[PriceObservation] = relationship(back_populates="retail_report")


class UserSubmission(Base):
    __tablename__ = "user_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(128))
    submission_type: Mapped[str] = mapped_column(String(64), nullable=False)
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    store: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(128))
    date_seen: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    receipt_asset_url: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(32), default=ModeratorStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ItemMatchReview(Base):
    __tablename__ = "item_match_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey("price_observations.id"), nullable=False, index=True)
    proposed_product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), index=True)
    reviewer_decision: Mapped[str] = mapped_column(String(32), default=ReviewDecision.NEEDS_REVIEW)
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    observation: Mapped[PriceObservation] = relationship(back_populates="match_reviews")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    retail_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    retail_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    retail_best_known: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    ask_median: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    ask_low: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    ask_high: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    sold_median_30d: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    sold_median_90d: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    sample_size_asks: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sample_size_solds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    premium_vs_retail_pct: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    premium_vs_retail_abs: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    freshness_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    product: Mapped[Product] = relationship(back_populates="metrics")


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    discovered_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parsed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    source: Mapped[Source] = relationship(back_populates="scrape_runs")
    errors: Mapped[list[ScrapeError]] = relationship(back_populates="scrape_run", cascade="all, delete-orphan")


class ScrapeError(Base):
    __tablename__ = "scrape_errors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scrape_run_id: Mapped[int] = mapped_column(ForeignKey("scrape_runs.id"), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    item_reference: Mapped[str | None] = mapped_column(String(255))
    error_type: Mapped[str] = mapped_column(String(64), nullable=False)
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    html_snapshot_path: Mapped[str | None] = mapped_column(String(1024))
    screenshot_path: Mapped[str | None] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    scrape_run: Mapped[ScrapeRun] = relationship(back_populates="errors")


class LegacyImportRow(Base):
    __tablename__ = "legacy_import_rows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_name: Mapped[str] = mapped_column(String(128), nullable=False, default="legacy_csv")
    external_row_id: Mapped[str | None] = mapped_column(String(255), index=True)
    raw_item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category_hint: Mapped[str | None] = mapped_column(String(64))
    price_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024))
    store: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(128))
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    proof_type: Mapped[str | None] = mapped_column(String(64))
    proof_asset_url: Mapped[str | None] = mapped_column(String(1024))
    duplicate_group_key: Mapped[str | None] = mapped_column(String(255), index=True)
    extraction_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.700"), nullable=False)
    price_confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.650"), nullable=False)
    publish_status: Mapped[str] = mapped_column(String(32), default="staged", nullable=False)
    raw_payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    watchlist_id: Mapped[int | None] = mapped_column(ForeignKey("watchlists.id"), index=True)
    alert_type: Mapped[str] = mapped_column(String(64), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_identifier: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    target_type: Mapped[str] = mapped_column(String(64), nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(64))
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

