# DECISIONS

## 2026-04-13

### Repository shape
Decision: Use a structured monorepo with `apps/api` and `apps/web`, plus `docs`, `infra`, `scripts`, and `tests`.
Rationale: The product spans web, API, ingestion, background jobs, and admin tooling. A monorepo keeps schema, adapters, docs, and UI aligned.

### Observation-first data model
Decision: Model prices as evidence in `price_observations` and derive metrics in `metric_snapshots`.
Rationale: Chrome Hearts price data is fragmented and often community-reported, so observations are more honest and extensible than direct product prices.

### MVP admin auth
Decision: Start with token-backed admin authentication suitable for internal/admin MVP usage.
Rationale: This provides meaningful protection for admin routes now while keeping the implementation lightweight enough for a first production-minded release.

### Source implementation policy
Decision: Implement source adapters behind shared abstractions and explicit source kill switches, and document uncertain integrations instead of pretending they are production-complete.
Rationale: Source stability varies widely; the product must degrade safely and transparently.

### Admin web protection
Decision: Protect `/admin` in the Next.js app with a signed HTTP-only session cookie issued from an admin login flow, while keeping backend admin endpoints token-protected.
Rationale: The web app fetches privileged moderation data server-side, so route protection must exist at the app layer as well as the API layer.

### Web mock fallback
Decision: Allow the web app to fall back to local mock data when `NEXT_PUBLIC_ENABLE_MOCK_DATA=true` or when the API is unavailable during local UI work.
Rationale: This keeps the frontend usable for styling and iteration without pretending that the backend has been verified in environments where it cannot currently run.

### Sold comp honesty
Decision: Do not seed or imply real sold-comp coverage where no reliable integrated sold source exists yet.
Rationale: Sample data must not overstate source support or mislabel reseller asks as sold evidence.

### Split server and browser API base URLs
Decision: Use `API_BASE_URL` for server-side Next.js requests and `NEXT_PUBLIC_API_BASE_URL` for browser requests.
Rationale: In Docker and production-like environments, the web server and the browser do not share the same network path to the API.

### Edge-safe admin session signing
Decision: Use Web Crypto-compatible HMAC signing for admin session cookies.
Rationale: Next.js middleware runs in an edge-style runtime, so route protection should avoid Node-only crypto assumptions.

### Admin matching workflow
Decision: Surface conservative ranked match candidates directly in the unmatched-observation admin flow, while still requiring explicit admin confirmation.
Rationale: This speeds up review without silently auto-linking ambiguous products.

### Source operations workflow
Decision: Treat source refresh as an admin-triggered and worker-callable operation that always writes `scrape_runs` and `scrape_errors`, even for disabled or stubbed sources.
Rationale: Operational visibility matters as much as successful ingestion; disabled, stubbed, and failed runs should remain visible instead of silently disappearing from admin history.

### Scrape failure inspection workflow
Decision: Expose scrape failures through a dedicated admin scrape-run detail read path backed directly by `scrape_errors`, rather than hiding them behind aggregate counters alone.
Rationale: Operators need to distinguish empty runs, policy stubs, and true parser failures quickly, and persisted error records are the most honest source of that detail.

### Duplicate review workflow
Decision: Review duplicate observations as grouped evidence records keyed by `duplicate_group_key`, with explicit admin reject or restore actions rather than silent auto-deduplication.
Rationale: Duplicate grouping is heuristic and should help operators prevent double-counting without deleting evidence or pretending the grouping logic is perfectly authoritative.

### Artifact preview workflow
Decision: Store local scrape-failure HTML snapshots under a configured artifact root and preview them through protected admin APIs/pages rather than exposing raw filesystem paths directly.
Rationale: Operators need to inspect failure artifacts, but arbitrary path exposure is unsafe and object storage delivery is not yet fully implemented.

### Duplicate keeper resolution workflow
Decision: Resolve duplicate groups by explicitly selecting one keeper observation, conservatively recommending a keeper, and rejecting the rest instead of silently merging evidence rows.
Rationale: Duplicate grouping is heuristic, so the system should help reviewers collapse obvious double-counts without pretending the grouped observations are interchangeable or auto-merging their product and proof metadata.

### Local submission proof upload workflow
Decision: Accept proof uploads through a validated local upload endpoint that stores receipt images and PDFs under a dedicated submission upload root, while leaving object-storage-backed signed uploads as a later enhancement.
Rationale: The MVP needs a real proof path now for submission trust and admin review, but external object storage has not been fully wired or runtime-validated in this environment.

### Admin catalog lookup workflow
Decision: Keep conservative ranked candidates as the default moderation assist, but add explicit free-text catalog lookup inside unmatched-observation and submission review flows.
Rationale: Ranked suggestions help speed up common matches, while manual search is necessary when aliases or noisy titles fall outside the top-ranked shortlist and reviewers still need safe, explicit control.

### Admin observation inspection workflow
Decision: Expose a dedicated admin observation-detail view that keeps the normalized observation, raw payload, proof references, ranked candidates, and match-review history together in one place.
Rationale: Admin review is evidence work, so operators need the full context of an observation without jumping between product pages, queue cards, and database assumptions.

### Public browse filtering workflow
Decision: Drive public browse and search from one shared catalog query service that filters by category, source class, market side, and minimum confidence using active observations plus latest metric snapshots, then sorts in application code for the current MVP-sized catalog.
Rationale: The product needs honest source-aware discovery now, and the current seeded catalog is small enough that a shared Python sort/filter layer is simpler and safer than prematurely introducing opaque SQL ranking logic.

### Public browse facet-count workflow
Decision: Expose public browse totals, pagination metadata, and facet counts from a dedicated browse response, and compute facet counts by dropping only the facet dimension being counted while preserving the rest of the current filter context.
Rationale: Collectors need to understand available catalog breadth without losing the current query posture, and self-excluding facet counts are more useful than counts taken only from the already-selected subset.

### Public browse URL-state workflow
Decision: Treat the public browse URL as a shareable serialization of the current browse filters, sort, and pagination offset, with the client hydrating from server-parsed search params and then keeping the URL synchronized as state changes.
Rationale: Collectors and internal operators need to share exact discovery views, and URL-backed state is the simplest honest MVP mechanism without introducing saved-search infrastructure yet.

### Public browse quick-view workflow
Decision: Layer explicit copy-link controls and a small curated set of browse quick views on top of the URL-backed browse state instead of jumping straight to user-defined saved-search persistence.
Rationale: The MVP needs obvious, reusable collector workflows now, and curated presets plus shareable URLs deliver most of that value without adding premature persistence and account-scoped state management.

### Web runtime validation workflow
Decision: Keep the React Compiler enabled in the Next.js app, but make runtime validation honest by installing the required `babel-plugin-react-compiler` dependency instead of silently disabling the compiler when the first production build fails.
Rationale: The repo is already opting into the compiler, so the production-minded fix is to satisfy that contract and verify the build path rather than masking the missing dependency.
