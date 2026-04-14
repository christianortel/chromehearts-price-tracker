# Local Development

## Requirements

- Docker Desktop
- Node.js 20+
- Python 3.12 if running the API outside Docker

## Quick start

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Run migrations inside the API container or with a local Python environment.
4. Seed starter records.
5. For frontend-only work without a running API, set `NEXT_PUBLIC_ENABLE_MOCK_DATA=true`.

## Notes

- The current committed setup favors Docker because the present shell environment does not have a working Python runtime.
- Source adapters are individually kill-switchable via environment and source metadata.
- Admin access uses the configured `ADMIN_TOKEN`.
- The Next.js admin route is separately protected by a signed session cookie derived from `ADMIN_SESSION_SECRET`.
- In Docker, use `API_BASE_URL=http://api:8000` for server-side web requests and `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` for browser requests.
- Local scrape snapshots and screenshots are stored under `ARTIFACT_STORAGE_ROOT` and previewed through protected admin routes.
- Local submission proof uploads are stored under `SUBMISSION_UPLOAD_ROOT`; uploaded proofs can be previewed from the protected admin UI.
