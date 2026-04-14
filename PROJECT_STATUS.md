# PROJECT STATUS

Last updated: 2026-04-13

## Current State Summary

- Repo structure, docs, initial migration, seed path, core API routes, source adapters, and backend tests exist.
- The public Next.js app shell and the admin surface are implemented, including manual matching, alias management, source operations controls, scrape-run inspection, duplicate review with keeper resolution, local artifact preview, and local submission proof upload.
- The backend now persists scrape runs and scrape errors through the shared source execution path and exposes drilldown APIs for persisted failures, heuristic duplicate groups, and local snapshot preview; the remaining major gaps are runtime validation, object-storage-backed delivery, and live selector confidence.
- Duplicate review now supports conservative keeper recommendation and explicit single-keeper resolution; deeper merge semantics remain deferred.
- The user submission flow now supports local proof uploads, but object-storage-backed delivery and broader runtime verification are still outstanding.
- Admin moderation now supports free-text product lookup inside unmatched-observation and submission review, layered on top of conservative ranked candidates, and observation detail inspection exposes raw payload and review context directly in the web admin.
- The public browse/search surface now supports real query, category, source-class, market-side, confidence-threshold, sorting, facet counts, page metadata, shareable URL-backed filter state, explicit share controls, and curated quick views backed by the shared catalog query layer; deeper runtime validation remains future work.
- The web workspace has now been partially runtime-validated locally through root `npm` scripts: dependency install, lint, and production build succeed, while the Python/API stack remains blocked in this shell.
- Current known risk: full-stack runtime validation is still incomplete because Python and Docker are unavailable locally.

## Active Focus For This Run

- validating the runtime path wherever local tooling actually exists
- fixing concrete web build issues surfaced by real local execution
- leaving the next handoff focused on remaining runtime blockers and follow-up hardening

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
- local runtime verification
- admin UX breadth
- adapter live-source validation

Stubbed:
- Reddit adapter
- Justin Reed adapter
- StockX adapter
- sold-comp source integrations pending compliant reliable access

Blocked:
- local execution and test runs are blocked in the current shell because Python 3.12 is not installed or not available on PATH

Remaining:
- run the full backend and web stacks in a Python-enabled environment
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
- installed the missing React Compiler Babel plugin so the Next.js workspace satisfies its configured compiler contract during real builds
- used the root workspace scripts to validate the web toolchain locally, then fixed the lint/build issues surfaced in admin asset preview and admin dashboard copy
- changed the web `typecheck` script to use Next compile mode so clean-checkout validation generates required route types instead of depending on stale `.next` artifacts

What remains:
- execute the stack and test suite in an environment with Python available
- add object-storage-backed delivery for submission proofs and scrape artifacts, plus richer screenshot browsing
- validate live source execution against real pages and tune selector resilience
- refine duplicate tooling with deeper merge semantics and reviewer notes where appropriate
- add user-defined saved browse views beyond the current curated quick views, then finish remaining docs and hardening work

Recommended next step:
- run `docker compose up --build`, `make migrate`, `make seed`, and the API/web test suites in a Python-capable environment, then fix any runtime issues before expanding source breadth or deepening object-storage delivery

Blockers or risks:
- this shell still lacks Python, so runtime verification remains outstanding
- Docker is also unavailable in this shell, so container-based validation cannot currently replace the missing Python toolchain
- parser implementations are fixture-validated and admin-inspectable, but still need live selector validation before claiming operational reliability
- duplicate grouping and keeper recommendation are heuristic and intentionally conservative; they still need runtime validation before being treated as operationally complete
- proof uploads and artifact preview currently support local stored files with safe validation and admin-only preview; object storage delivery and larger binary handling remain future work
- the public web workspace now passes local lint and production build via the root npm scripts, but the API-backed and seeded-data flows still need runtime validation before being treated as production-ready
