from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import ScrapeRun, Source
from app.schemas.sources import SourceOut

router = APIRouter(tags=["sources"])


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)) -> list[SourceOut]:
    sources = db.query(Source).order_by(Source.name.asc()).all()
    return [SourceOut.model_validate(source) for source in sources]


@router.get("/sources/health")
def source_health_public(db: Session = Depends(get_db)) -> list[dict]:
    latest_runs = (
        db.query(
            Source.id.label("source_id"),
            Source.name.label("source_name"),
            Source.enabled.label("enabled"),
            func.max(ScrapeRun.finished_at).label("last_finished_at"),
        )
        .outerjoin(ScrapeRun, ScrapeRun.source_id == Source.id)
        .group_by(Source.id)
        .all()
    )
    return [dict(row._mapping) for row in latest_runs]

