# Deployment

## Containers

- `api`: FastAPI + Alembic runtime
- `worker`: Celery worker
- `web`: Next.js application
- `postgres`, `redis`: stateful dependencies

## Environment

- secrets are provided via environment variables only
- Sentry can be enabled with `SENTRY_DSN`
- admin session and API tokens must be rotated outside the repo
- local submission uploads and scrape artifacts should be mounted to persistent volumes until object storage delivery is implemented

## Operational advice

- keep source kill switches available in the database and environment
- monitor parser error rates after deployments
- recompute metrics after bulk imports or alias changes
