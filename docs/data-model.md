# Data Model

The core schema is observation-centric.

## Canonical entities

- `products`: canonical item families
- `product_aliases`: known naming variants used by matching
- `product_variants`: material, color, finish, and size-specific variants
- `sources`: per-source metadata and policy controls

## Evidence entities

- `price_observations`: normalized evidence records across retail reports, curated asks, marketplace asks, and sold comps
- `retail_reports`: retail-specific extension table for community or receipt-backed sightings
- `user_submissions`: inbound community submissions prior to moderation or publication; `receipt_asset_url` can reference either an external proof URL or a locally stored uploaded proof path
- `item_match_reviews`: manual review records for ambiguous observation mapping
- `legacy_import_rows`: staging records for imported historical spreadsheets

## Metrics and operations

- `metric_snapshots`: product-level derived metrics with explicit sample sizes
- `scrape_runs`: per-source run tracking
- `scrape_errors`: parser, fetch, or workflow failures
- `watchlists`, `alerts`, `admin_audit_logs`: user and admin operations

Metrics never collapse retail, ask, and sold evidence into a single ambiguous statistic.
