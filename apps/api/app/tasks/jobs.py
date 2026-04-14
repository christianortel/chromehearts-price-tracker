from __future__ import annotations

from celery.utils.log import get_task_logger

from app.db.session import SessionLocal
from app.models import Product, Source
from app.services.metrics.engine import recompute_product_metrics
from app.services.operations.source_runs import execute_source_run
from app.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="metrics.recompute_all")
def recompute_all_metrics_task() -> dict[str, int]:
    with SessionLocal() as db:
        product_ids = [row.id for row in db.query(Product.id).all()]
        for product_id in product_ids:
            recompute_product_metrics(db, product_id)
        db.commit()
        logger.info("metrics recomputed", extra={"product_count": len(product_ids)})
        return {"product_count": len(product_ids)}


@celery_app.task(name="sources.health_check")
def source_health_check_task() -> dict[str, int]:
    with SessionLocal() as db:
        enabled_count = db.query(Source).filter(Source.enabled.is_(True)).count()
        logger.info("source health check completed", extra={"enabled_sources": enabled_count})
        return {"enabled_sources": enabled_count}


@celery_app.task(name="sources.refresh")
def source_refresh_task(source_name: str, query: str = "chrome hearts") -> dict[str, int | str]:
    with SessionLocal() as db:
        result = execute_source_run(db, source_name, query=query)
        db.commit()
        logger.info(
            "source refresh completed",
            extra={
                "source_name": source_name,
                "status": result.run.status,
                "discovered_count": result.discovered_count,
                "inserted_count": result.inserted_count,
                "error_count": result.error_count,
            },
        )
        return {
            "source_name": source_name,
            "status": result.run.status,
            "discovered_count": result.discovered_count,
            "inserted_count": result.inserted_count,
            "error_count": result.error_count,
        }


@celery_app.task(name="sources.refresh_enabled")
def refresh_enabled_sources_task(query: str = "chrome hearts") -> dict[str, int]:
    with SessionLocal() as db:
        source_names = [row.name for row in db.query(Source).filter(Source.enabled.is_(True)).all()]
        success_count = 0
        for source_name in source_names:
            result = execute_source_run(db, source_name, query=query)
            if result.run.status == "success":
                success_count += 1
        db.commit()
        logger.info(
            "enabled source refresh completed",
            extra={"source_count": len(source_names), "success_count": success_count},
        )
        return {"source_count": len(source_names), "success_count": success_count}
