# Architecture

Chrome Hearts Price Intelligence is built as a data platform first. Raw source records are normalized into an observation contract, reviewed or auto-matched to canonical products, and aggregated into source-aware metrics snapshots for the public product UI and admin operations.

## Major components

- Next.js 15 web application for public browse/search, product detail, submissions, and admin tools.
- FastAPI service for REST APIs, admin actions, ingestion orchestration, and metrics recomputation.
- PostgreSQL for canonical products, observations, review workflows, metrics snapshots, and scrape logs.
- Redis and Celery for scheduled source refreshes, metrics jobs, and health checks.
- Adapter framework for manual imports, static scraping, and browser-automation-capable sources.
- Local submission proof uploads are validated at ingest time and stored separately from scrape failure artifacts.
- Admin access is protected in both the API and web layers.
- Admin review tooling includes candidate-ranked matching with free-text catalog lookup, observation-detail inspection with raw payload context, alias management, source controls, scrape-run error inspection, duplicate observation review with keeper resolution, and protected artifact preview.
- Public browse and public search now share a catalog query layer that filters conservatively against active observations and latest product metrics rather than inventing blended price signals.
- Public browse metadata exposes totals, basic pagination state, and facet counts computed from the same shared query layer so the discovery UI does not guess at catalog size or available filter breadth.
- The browse page now syncs filter and pagination state into the URL so shared links preserve the same discovery posture across reloads and handoffs.
- Public browse also exposes explicit copy-link controls and curated quick-view presets so sharing and common collector workflows do not depend on users manually editing URLs.

## Data flow

1. A source adapter discovers candidate items or a CSV importer stages legacy rows.
2. Raw records are normalized into a common observation payload.
3. Matching services attempt deterministic and scored mapping to canonical products.
4. Low-confidence or unmatched records remain reviewable in admin queues.
5. Approved observations flow into product evidence timelines and metrics snapshots.
6. The web app surfaces retail, ask, and sold evidence separately, with freshness and confidence.
7. Admin users authenticate in the web app before the server fetches privileged moderation data.

## Design principles

- Prices are observations, not authoritative truth.
- Retail, ask, and sold metrics stay separate.
- Confidence is multi-dimensional: extraction, matching, and price trust.
- Every source is kill-switchable.
- The admin workflow is a core feature, not a sidecar.
