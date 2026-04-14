from decimal import Decimal

from app.models import MetricSnapshot, Product
from app.services.metrics.engine import recompute_product_metrics
from sqlalchemy.orm import Session


def test_metrics_recompute_keeps_retail_and_ask_separate(db_session: Session) -> None:
    product = db_session.query(Product).first()
    assert product is not None
    snapshot = recompute_product_metrics(db_session, product.id)
    assert snapshot.retail_best_known is not None
    assert snapshot.ask_median is not None
    assert snapshot.sold_median_30d is None
    assert snapshot.premium_vs_retail_abs is not None
    assert snapshot.ask_median > snapshot.retail_best_known
    assert isinstance(snapshot.premium_vs_retail_pct, Decimal)


def test_metrics_snapshot_upserts_for_same_day(db_session: Session) -> None:
    product = db_session.query(Product).first()
    assert product is not None
    recompute_product_metrics(db_session, product.id)
    recompute_product_metrics(db_session, product.id)
    count = db_session.query(MetricSnapshot).filter(MetricSnapshot.product_id == product.id).count()
    assert count == 1
