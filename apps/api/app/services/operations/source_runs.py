from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import ScrapeError, ScrapeRun, Source
from app.services.adapters.registry import build_adapter_registry
from app.services.artifacts import write_scrape_html_snapshot
from app.services.etl.pipeline import persist_observations


@dataclass
class SourceRunResult:
    run: ScrapeRun
    discovered_count: int
    inserted_count: int
    error_count: int


def execute_source_run(
    db: Session,
    source_name: str,
    *,
    query: str = "chrome hearts",
    html_override: str | None = None,
) -> SourceRunResult:
    source = db.query(Source).filter(Source.name == source_name).one_or_none()
    if source is None:
        raise ValueError(f"Unknown source: {source_name}")

    run = ScrapeRun(source_id=source.id, status="running", notes=f"query={query}")
    db.add(run)
    db.flush()

    if not source.enabled:
        run.status = "disabled"
        run.notes = "Source disabled by policy toggle."
        run.finished_at = datetime.now(UTC)
        db.flush()
        return SourceRunResult(run=run, discovered_count=0, inserted_count=0, error_count=0)

    adapter = build_adapter_registry().get(source_name)
    if adapter is None:
        run.status = "unsupported"
        run.notes = "No adapter is registered for this source."
        run.finished_at = datetime.now(UTC)
        db.flush()
        return SourceRunResult(run=run, discovered_count=0, inserted_count=0, error_count=0)

    html: str | None = None
    try:
        if html_override is None:
            discovery_url = adapter.build_discovery_url(query)
            html = asyncio.run(adapter.fetch_text(discovery_url))
        else:
            html = html_override

        discovered_items = adapter.parse_listing_page(html)
        run.discovered_count = len(discovered_items)
        observations = adapter.to_observations(discovered_items)
        persisted = persist_observations(db, observations, scrape_run=run)
        run.status = "success"
        run.notes = f"query={query}; discovered={len(discovered_items)}; inserted={len(persisted)}"
        run.finished_at = datetime.now(UTC)
        db.flush()
        return SourceRunResult(
            run=run,
            discovered_count=len(discovered_items),
            inserted_count=len(persisted),
            error_count=run.error_count,
        )
    except NotImplementedError as exc:
        run.status = "stubbed"
        run.error_count += 1
        run.notes = f"query={query}; adapter not implemented"
        db.add(
            ScrapeError(
                scrape_run_id=run.id,
                source_id=source.id,
                error_type="not_implemented",
                error_message=str(exc),
            )
        )
    except Exception as exc:  # noqa: BLE001
        run.status = "error"
        run.error_count += 1
        run.notes = f"query={query}; failed with {exc.__class__.__name__}"
        html_snapshot_path = None
        if html:
            try:
                html_snapshot_path = write_scrape_html_snapshot(
                    source_name=source.name, run_id=run.id, html=html
                )
            except OSError:
                html_snapshot_path = None
        db.add(
            ScrapeError(
                scrape_run_id=run.id,
                source_id=source.id,
                error_type=exc.__class__.__name__,
                error_message=str(exc),
                html_snapshot_path=html_snapshot_path,
            )
        )
    run.finished_at = datetime.now(UTC)
    db.flush()
    return SourceRunResult(
        run=run,
        discovered_count=run.discovered_count,
        inserted_count=run.inserted_count,
        error_count=run.error_count,
    )


def set_source_enabled(db: Session, source_id: int, enabled: bool) -> Source:
    source = db.query(Source).filter(Source.id == source_id).one_or_none()
    if source is None:
        raise ValueError(f"Unknown source id: {source_id}")
    source.enabled = enabled
    db.flush()
    return source
