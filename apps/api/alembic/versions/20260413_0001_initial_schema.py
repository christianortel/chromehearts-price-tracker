"""initial schema

Revision ID: 20260413_0001
Revises: None
Create Date: 2026-04-13 19:30:00
"""

import sqlalchemy as sa
from alembic import op

revision = "20260413_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("subcategory", sa.String(length=128), nullable=True),
        sa.Column("material", sa.String(length=128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_products_canonical_name", "products", ["canonical_name"], unique=True)
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_category", "products", ["category"], unique=False)

    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("base_url", sa.String(length=512), nullable=True),
        sa.Column("crawl_method", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("policy_status", sa.String(length=64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sources_name", "sources", ["name"], unique=True)

    op.create_table(
        "product_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("alias_text", sa.String(length=255), nullable=False),
        sa.Column("alias_type", sa.String(length=64), nullable=False),
        sa.Column("source_name", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_product_aliases_product_id", "product_aliases", ["product_id"], unique=False
    )
    op.create_index(
        "ix_product_aliases_alias_text", "product_aliases", ["alias_text"], unique=False
    )

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("size", sa.String(length=64), nullable=True),
        sa.Column("color", sa.String(length=64), nullable=True),
        sa.Column("finish", sa.String(length=64), nullable=True),
        sa.Column("material_detail", sa.String(length=128), nullable=True),
        sa.Column("variant_key", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_product_variants_product_id", "product_variants", ["product_id"], unique=False
    )
    op.create_index(
        "ix_product_variants_variant_key", "product_variants", ["variant_key"], unique=True
    )

    op.create_table(
        "user_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("submission_type", sa.String(length=64), nullable=False),
        sa.Column("item_name", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("store", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("date_seen", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("receipt_asset_url", sa.String(length=1024), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "legacy_import_rows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(length=128), nullable=False),
        sa.Column("external_row_id", sa.String(length=255), nullable=True),
        sa.Column("raw_item_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_title", sa.String(length=255), nullable=False),
        sa.Column("category_hint", sa.String(length=64), nullable=True),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("store", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("proof_type", sa.String(length=64), nullable=True),
        sa.Column("proof_asset_url", sa.String(length=1024), nullable=True),
        sa.Column("duplicate_group_key", sa.String(length=255), nullable=True),
        sa.Column("extraction_confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("price_confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("publish_status", sa.String(length=32), nullable=False),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_legacy_import_rows_external_row_id",
        "legacy_import_rows",
        ["external_row_id"],
        unique=False,
    )
    op.create_index(
        "ix_legacy_import_rows_normalized_title",
        "legacy_import_rows",
        ["normalized_title"],
        unique=False,
    )
    op.create_index(
        "ix_legacy_import_rows_duplicate_group_key",
        "legacy_import_rows",
        ["duplicate_group_key"],
        unique=False,
    )

    op.create_table(
        "watchlists",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_watchlists_user_id", "watchlists", ["user_id"], unique=False)
    op.create_index("ix_watchlists_product_id", "watchlists", ["product_id"], unique=False)

    op.create_table(
        "price_observations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("variant_id", sa.Integer(), sa.ForeignKey("product_variants.id"), nullable=True),
        sa.Column("raw_title", sa.String(length=512), nullable=False),
        sa.Column("normalized_title", sa.String(length=512), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("source_item_id", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=False),
        sa.Column("source_type_snapshot", sa.String(length=64), nullable=False),
        sa.Column("market_side", sa.String(length=32), nullable=False),
        sa.Column("seller_or_store", sa.String(length=255), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("condition", sa.String(length=128), nullable=True),
        sa.Column("size_text", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column("price_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("shipping_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("tax_included", sa.Boolean(), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("proof_type", sa.String(length=64), nullable=True),
        sa.Column("proof_asset_url", sa.String(length=1024), nullable=True),
        sa.Column("extraction_confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("match_confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("price_confidence", sa.Numeric(4, 3), nullable=False),
        sa.Column("duplicate_group_key", sa.String(length=255), nullable=True),
        sa.Column("raw_payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_price_observations_product_id", "price_observations", ["product_id"], unique=False
    )
    op.create_index(
        "ix_price_observations_variant_id", "price_observations", ["variant_id"], unique=False
    )
    op.create_index(
        "ix_price_observations_source_id", "price_observations", ["source_id"], unique=False
    )
    op.create_index(
        "ix_price_observations_source_item_id",
        "price_observations",
        ["source_item_id"],
        unique=False,
    )
    op.create_index(
        "ix_price_observations_normalized_title",
        "price_observations",
        ["normalized_title"],
        unique=False,
    )
    op.create_index(
        "ix_price_observations_market_side", "price_observations", ["market_side"], unique=False
    )
    op.create_index(
        "ix_price_observations_observed_at", "price_observations", ["observed_at"], unique=False
    )
    op.create_index(
        "ix_price_observations_duplicate_group_key",
        "price_observations",
        ["duplicate_group_key"],
        unique=False,
    )

    op.create_table(
        "retail_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "source_observation_id",
            sa.Integer(),
            sa.ForeignKey("price_observations.id"),
            nullable=False,
        ),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("store_name", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("receipt_submitted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("moderator_status", sa.String(length=32), nullable=False),
        sa.Column("moderator_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("source_observation_id"),
    )
    op.create_index("ix_retail_reports_product_id", "retail_reports", ["product_id"], unique=False)

    op.create_table(
        "item_match_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "observation_id", sa.Integer(), sa.ForeignKey("price_observations.id"), nullable=False
        ),
        sa.Column("proposed_product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("reviewer_decision", sa.String(length=32), nullable=False),
        sa.Column("reviewer_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_item_match_reviews_observation_id",
        "item_match_reviews",
        ["observation_id"],
        unique=False,
    )
    op.create_index(
        "ix_item_match_reviews_proposed_product_id",
        "item_match_reviews",
        ["proposed_product_id"],
        unique=False,
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("retail_low", sa.Numeric(12, 2), nullable=True),
        sa.Column("retail_high", sa.Numeric(12, 2), nullable=True),
        sa.Column("retail_best_known", sa.Numeric(12, 2), nullable=True),
        sa.Column("ask_median", sa.Numeric(12, 2), nullable=True),
        sa.Column("ask_low", sa.Numeric(12, 2), nullable=True),
        sa.Column("ask_high", sa.Numeric(12, 2), nullable=True),
        sa.Column("sold_median_30d", sa.Numeric(12, 2), nullable=True),
        sa.Column("sold_median_90d", sa.Numeric(12, 2), nullable=True),
        sa.Column("sample_size_asks", sa.Integer(), nullable=False),
        sa.Column("sample_size_solds", sa.Integer(), nullable=False),
        sa.Column("premium_vs_retail_pct", sa.Numeric(12, 4), nullable=True),
        sa.Column("premium_vs_retail_abs", sa.Numeric(12, 2), nullable=True),
        sa.Column("freshness_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_metric_snapshots_product_id", "metric_snapshots", ["product_id"], unique=False
    )
    op.create_index(
        "ix_metric_snapshots_snapshot_date", "metric_snapshots", ["snapshot_date"], unique=False
    )

    op.create_table(
        "scrape_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("discovered_count", sa.Integer(), nullable=False),
        sa.Column("parsed_count", sa.Integer(), nullable=False),
        sa.Column("inserted_count", sa.Integer(), nullable=False),
        sa.Column("error_count", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_scrape_runs_source_id", "scrape_runs", ["source_id"], unique=False)

    op.create_table(
        "scrape_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scrape_run_id", sa.Integer(), sa.ForeignKey("scrape_runs.id"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("item_reference", sa.String(length=255), nullable=True),
        sa.Column("error_type", sa.String(length=64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("html_snapshot_path", sa.String(length=1024), nullable=True),
        sa.Column("screenshot_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_scrape_errors_scrape_run_id", "scrape_errors", ["scrape_run_id"], unique=False
    )
    op.create_index("ix_scrape_errors_source_id", "scrape_errors", ["source_id"], unique=False)

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("watchlist_id", sa.Integer(), sa.ForeignKey("watchlists.id"), nullable=True),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "admin_audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_identifier", sa.String(length=128), nullable=False),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=False),
        sa.Column("target_id", sa.String(length=64), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_table("alerts")
    op.drop_index("ix_scrape_errors_source_id", table_name="scrape_errors")
    op.drop_index("ix_scrape_errors_scrape_run_id", table_name="scrape_errors")
    op.drop_table("scrape_errors")
    op.drop_index("ix_scrape_runs_source_id", table_name="scrape_runs")
    op.drop_table("scrape_runs")
    op.drop_index("ix_metric_snapshots_snapshot_date", table_name="metric_snapshots")
    op.drop_index("ix_metric_snapshots_product_id", table_name="metric_snapshots")
    op.drop_table("metric_snapshots")
    op.drop_index("ix_item_match_reviews_proposed_product_id", table_name="item_match_reviews")
    op.drop_index("ix_item_match_reviews_observation_id", table_name="item_match_reviews")
    op.drop_table("item_match_reviews")
    op.drop_index("ix_retail_reports_product_id", table_name="retail_reports")
    op.drop_table("retail_reports")
    op.drop_index("ix_price_observations_duplicate_group_key", table_name="price_observations")
    op.drop_index("ix_price_observations_observed_at", table_name="price_observations")
    op.drop_index("ix_price_observations_market_side", table_name="price_observations")
    op.drop_index("ix_price_observations_normalized_title", table_name="price_observations")
    op.drop_index("ix_price_observations_source_item_id", table_name="price_observations")
    op.drop_index("ix_price_observations_source_id", table_name="price_observations")
    op.drop_index("ix_price_observations_variant_id", table_name="price_observations")
    op.drop_index("ix_price_observations_product_id", table_name="price_observations")
    op.drop_table("price_observations")
    op.drop_index("ix_watchlists_product_id", table_name="watchlists")
    op.drop_index("ix_watchlists_user_id", table_name="watchlists")
    op.drop_table("watchlists")
    op.drop_index("ix_legacy_import_rows_duplicate_group_key", table_name="legacy_import_rows")
    op.drop_index("ix_legacy_import_rows_normalized_title", table_name="legacy_import_rows")
    op.drop_index("ix_legacy_import_rows_external_row_id", table_name="legacy_import_rows")
    op.drop_table("legacy_import_rows")
    op.drop_table("user_submissions")
    op.drop_index("ix_product_variants_variant_key", table_name="product_variants")
    op.drop_index("ix_product_variants_product_id", table_name="product_variants")
    op.drop_table("product_variants")
    op.drop_index("ix_product_aliases_alias_text", table_name="product_aliases")
    op.drop_index("ix_product_aliases_product_id", table_name="product_aliases")
    op.drop_table("product_aliases")
    op.drop_index("ix_sources_name", table_name="sources")
    op.drop_table("sources")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_slug", table_name="products")
    op.drop_index("ix_products_canonical_name", table_name="products")
    op.drop_table("products")
