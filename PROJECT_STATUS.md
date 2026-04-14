# PROJECT STATUS

Last updated: 2026-04-13

## Current State Summary

- Repo structure, docs, initial migration, seed path, core API routes, source adapters, and backend tests exist.
- The public Next.js app shell and the admin surface are implemented, including manual matching, alias management, source operations controls, scrape-run inspection, duplicate review with keeper resolution, local artifact preview, and local submission proof upload.
- The backend now persists scrape runs and scrape errors through the shared source execution path and exposes drilldown APIs for persisted failures, heuristic duplicate groups, and local snapshot preview; the remaining major gaps are runtime validation, object-storage-backed delivery, and live selector confidence.
- Duplicate review now supports conservative keeper recommendation and explicit single-keeper resolution; deeper merge semantics remain deferred.
- The user submission flow now supports local proof uploads, but object-storage-backed delivery and broader runtime verification are still outstanding.
- Admin moderation now supports free-text product lookup inside unmatched-observation and submission review, layered on top of conservative ranked candidates, and observation detail inspection exposes raw payload and review context directly in the web admin.
- The public browse/search surface now supports real query, category, source-class, market-side, confidence-threshold, sorting, facet counts, page metadata, shareable URL-backed filter state, explicit share controls, and curated quick views backed by the shared catalog query layer.
- The web workspace passes local validation through the root npm scripts for lint, compile-mode typecheck, and production build.
- The API workspace now passes the same core quality gates as GitHub Actions locally: `ruff check .`, `mypy app`, and `pytest`.
- Current known risk: Docker-based full-stack validation and live-source selector verification are still incomplete.

## Active Focus For This Run

- reproducing and fixing the failing GitHub Actions `CI / api` job locally
- tightening API lint, typing, seed, and metrics behavior until the local API quality gate is green
- leaving the next handoff focused on post-CI hardening instead of basic toolchain availability

## Milestone 1: Foundation

Status: Substantially complete

Completed:
- repository structure scaffolded
- root developer tooling files created
- environment variable template created
- Docker Compose baseline created
- initial documentation and project tracking files created
- FastAPI app shell, SQLAlchemy models, and API routes created
- Alembic environment and initial schema migration added
- seed generation added for 100+ canonical MVP products plus starter observations
- protected Next.js app shell added with home, browse, product, submission, and admin pages

Partially complete:
- Docker-based full-stack runtime verification
- admin UX breadth
- adapter live-source validation

Stubbed:
- Reddit adapter
- Justin Reed adapter
- StockX adapter
- sold-comp source integrations pending compliant reliable access

Blocked:
- Docker is still unavailable in this shell, so containerized end-to-end validation cannot be completed in-session

Remaining:
- run the full backend and web stacks in Docker
- validate migrations, seeds, and tests end to end
- deepen admin operations with object-storage-backed artifact delivery and duplicate merge tooling
- add more source coverage and hardening

## Milestone 2: Core Data Platform

Status: In progress

Completed:
- normalized observation contract implemented
- normalization and matching services added
- CSV staging importer service and publishing flow added
- metrics recomputation service added
- observation persistence pipeline added

Partially complete:
- ingestion scheduling and periodic policies
- richer manual review workflows

Stubbed:
- semantic fallback matching provider

## Milestone 3: First Real Data Sources

Status: In progress

Completed:
- eBay adapter implemented against parser fixture
- Rinkan adapter implemented against parser fixture
- source metadata and kill-switch-ready records seeded
- adapter tests added

Partially complete:
- live selector validation against real pages
- broader source coverage beyond eBay and Rinkan

## Milestone 4: Product UI

Status: In progress

Completed:
- dark-mode-first Next.js UI shell
- home page
- browse/search view
- real public browse filters for query, category, source class, market side, confidence threshold, and collector-facing sorting
- public browse totals, facet counts, and pagination controls
- shareable browse URL state for filters and pagination
- explicit copy-link control and curated quick views for browse state reuse
- product detail page with metric cards, confidence badge, chart, and evidence table
- submission page

Partially complete:
- source health and chart depth
- deeper pagination depth and user-defined saved browse views

## Milestone 5: Admin Operations

Status: In progress

Completed:
- admin route protection in web app
- unmatched observation dashboard
- submission moderation actions
- local submission proof upload endpoint and form flow
- metrics recompute action
- candidate-ranked manual product matching
- alias management APIs and admin UI
- source health dashboard
- manual source refresh triggers
- source enable/disable kill switches
- scrape run history view
- scrape run detail view with persisted error inspection
- duplicate observation review page and APIs
- duplicate keeper recommendation and one-click group resolution
- protected artifact preview for stored scrape snapshots
- admin inspection links for uploaded submission proofs
- free-text product lookup inside unmatched-observation and submission review
- admin observation detail pages with raw payload, proof context, and match-review history

Partially complete:
- deeper duplicate merge semantics
- richer admin catalog filters beyond the current free-text lookup

## Run Summary

Completed this run:
- reviewed the existing repo and status/docs before making changes
- reproduced the failing GitHub Actions `CI / api` job locally with a Python 3.12 virtual environment
- fixed the API runtime import break in rate limiting, tightened Ruff configuration for tests and Alembic, and cleaned up the API lint surface until `ruff check .` passed
- resolved the remaining mypy failures in catalog search, matching, seed typing, and admin serialization until `mypy app` passed
- fixed real API/runtime defects exposed by pytest, including timezone-safe freshness scoring, zip-up category precedence, fuller cross-category seed coverage, a seeded unmatched moderation example, flush-safe retail-report creation, and admin observation-detail payload construction
- ran the full API pytest suite successfully and verified that all 33 API tests pass locally

What remains:
- execute the stack end to end in Docker
- add object-storage-backed delivery for submission proofs and scrape artifacts, plus richer screenshot browsing
- validate live source execution against real pages and tune selector resilience
- refine duplicate tooling with deeper merge semantics and reviewer notes where appropriate
- add user-defined saved browse views beyond the current curated quick views, then finish remaining docs and hardening work

Recommended next step:
- rerun GitHub Actions on the pushed CI fix, then run `docker compose up --build`, `make migrate`, `make seed`, and the full stack smoke path to validate containerized execution before expanding source breadth or deepening object-storage delivery

Blockers or risks:
- Docker is still unavailable in this shell, so container-based validation remains outstanding even though the local Python/API quality gate now passes
- parser implementations are fixture-validated and admin-inspectable, but still need live selector validation before claiming operational reliability
- duplicate grouping and keeper recommendation are heuristic and intentionally conservative; they still need runtime validation before being treated as operationally complete
- proof uploads and artifact preview currently support local stored files with safe validation and admin-only preview; object storage delivery and larger binary handling remain future work
- the public web workspace passes local lint and production build, and the API workspace passes local lint, typing, and tests, but Dockerized stack validation and live-source execution still need to be completed before treating the system as production-ready
