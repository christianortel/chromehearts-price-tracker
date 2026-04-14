# Chrome Hearts Price Intelligence

Chrome Hearts Price Intelligence is a pricing evidence platform for fragmented Chrome Hearts retail, resale, and community-reported market data. The system treats every price as an observation with timestamp, source context, freshness, extraction confidence, match confidence, and price confidence.

This repository contains:

- `apps/api`: FastAPI backend, SQLAlchemy models, Alembic migrations, ingestion pipeline, matching engine, metrics engine, and admin APIs.
- `apps/web`: Next.js 15 frontend for search, browse, product detail, submissions, and admin operations.
- `docs`: architecture, data model, source policy, metrics, matching, importer, and operations documentation.
- `tests`: end-to-end tests and shared test data.
- `infra`: Dockerfiles and deployment support.

## MVP scope

Supported categories for the MVP:

- trucker hats
- hoodies
- zip-ups
- long sleeves
- common rings
- common bracelets

Deliberately not optimized in MVP:

- exotic leather
- custom or one-off pieces
- ultra-rare furniture and archive items
- computer vision matching
- tax-accurate global retail harmonization

## Current state

The repository is scaffolded to support:

- observation-centric relational data model
- CSV legacy import staging
- source adapters with normalized observation outputs
- metrics snapshots separated into retail, ask, and sold views
- admin review queues for unmatched and low-confidence data
- premium, freshness, and confidence surfacing in the product UI
- protected admin dashboard in the web app

The current implementation now includes:

- initial Alembic schema migration
- seed generation for 100+ canonical MVP products
- sample source, alias, variant, retail, and ask data for local development
- legacy CSV staging importer script
- eBay and Rinkan parser adapters backed by fixture tests
- public and admin web pages built in Next.js 15
- local submission proof upload with validation for receipt images and PDFs
- persisted scrape-run logging, source health summaries, and admin source controls for manual refresh and kill switches
- admin scrape-run detail views for persisted parse failures and adapter stub errors
- admin duplicate observation review with recommended keepers and one-click keeper resolution for heuristic duplicate groups
- free-text catalog lookup inside unmatched-observation and submission review flows, layered on top of conservative ranked candidates
- admin observation detail pages with raw payload, proof inspection, ranked candidates, and match-review history
- protected admin artifact preview for stored HTML snapshots and screenshots
- public browse filters for query, category, source class, market side, confidence threshold, and collector-facing sorting
- public browse totals, facet counts, and pagination controls backed by shared catalog metadata
- shareable URL-backed public browse state for filters and pagination
- explicit public browse share controls and curated quick-view presets layered on top of the URL-backed browse state
- local API verification against the GitHub Actions quality gate: Ruff, mypy, and pytest all pass from the checked-in API workspace config

See `PROJECT_STATUS.md` for active progress, `DECISIONS.md` for architecture and product decisions, and `TODO_BACKLOG.md` for deferred work.

## Local development

1. Copy `.env.example` to `.env`.
2. Start infrastructure with `docker compose up --build`.
3. Run migrations with `make migrate`.
4. Seed starter data with `make seed`.
5. Open the web app at `http://localhost:3000`.
6. Open the API docs at `http://localhost:8000/docs`.
7. Validate the web workspace with `npm install`, `npm run lint:web`, `npm run typecheck:web`, and `npm run build:web`.
8. Validate the API workspace with `python -m venv .venv`, `.venv\Scripts\pip.exe install -r apps/api/requirements.txt`, then from `apps/api` run `..\..\.venv\Scripts\ruff.exe check .`, `..\..\.venv\Scripts\mypy.exe app`, and `..\..\.venv\Scripts\pytest.exe`.

When running in Docker, the web server uses `API_BASE_URL` for server-side requests and the browser uses `NEXT_PUBLIC_API_BASE_URL`.

This workspace has now been locally validated in-session for both web and API quality gates. Web lint, compile-mode typecheck, and production build pass, and the API Ruff, mypy, and pytest suite pass against a local Python 3.12 virtual environment. Docker-based full-stack validation and live-source execution against real pages still remain outstanding.
