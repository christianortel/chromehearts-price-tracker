from decimal import Decimal

from app.db.session import get_db
from app.models import MetricSnapshot, PriceObservation, Product
from app.schemas.common import MetricSnapshotOut
from app.schemas.products import (
    ObservationOut,
    ProductBrowseResponse,
    ProductDetail,
    ProductListItem,
)
from app.services.catalog_search import (
    ProductBrowseSort,
    browse_catalog_products,
    latest_metric_for_product,
    query_catalog_products,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/products", tags=["products"])


def _latest_metric(product: Product) -> MetricSnapshot | None:
    return latest_metric_for_product(product)


@router.get("", response_model=list[ProductListItem])
def list_products(
    q: str | None = Query(default=None, min_length=1),
    category: str | None = Query(default=None),
    categories: list[str] = Query(default=[]),
    source_types: list[str] = Query(default=[]),
    market_sides: list[str] = Query(default=[]),
    min_confidence: Decimal | None = Query(default=None, ge=0, le=1),
    sort: ProductBrowseSort = Query(default="updated_desc"),
    limit: int = Query(default=200, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[ProductListItem]:
    merged_categories = [*categories]
    if category and category not in merged_categories:
        merged_categories.append(category)
    return query_catalog_products(
        db,
        query=q,
        categories=merged_categories or None,
        source_types=source_types or None,
        market_sides=market_sides or None,
        min_confidence=min_confidence,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/browse", response_model=ProductBrowseResponse)
def browse_products(
    q: str | None = Query(default=None, min_length=1),
    category: str | None = Query(default=None),
    categories: list[str] = Query(default=[]),
    source_types: list[str] = Query(default=[]),
    market_sides: list[str] = Query(default=[]),
    min_confidence: Decimal | None = Query(default=None, ge=0, le=1),
    sort: ProductBrowseSort = Query(default="updated_desc"),
    limit: int = Query(default=12, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ProductBrowseResponse:
    merged_categories = [*categories]
    if category and category not in merged_categories:
        merged_categories.append(category)
    return browse_catalog_products(
        db,
        query=q,
        categories=merged_categories or None,
        source_types=source_types or None,
        market_sides=market_sides or None,
        min_confidence=min_confidence,
        sort=sort,
        limit=limit,
        offset=offset,
    )


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDetail:
    product = db.query(Product).filter(Product.id == product_id).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    observations = (
        db.query(PriceObservation)
        .filter(PriceObservation.product_id == product_id)
        .order_by(PriceObservation.observed_at.desc())
        .limit(100)
        .all()
    )
    return ProductDetail(
        **product.__dict__,
        latest_metric=MetricSnapshotOut.model_validate(_latest_metric(product))
        if _latest_metric(product)
        else None,
        observations=[ObservationOut.model_validate(observation) for observation in observations],
        aliases=[alias.alias_text for alias in product.aliases],
    )


@router.get("/{product_id}/observations", response_model=list[ObservationOut])
def get_product_observations(
    product_id: int, db: Session = Depends(get_db)
) -> list[ObservationOut]:
    observations = (
        db.query(PriceObservation)
        .filter(PriceObservation.product_id == product_id)
        .order_by(PriceObservation.observed_at.desc())
        .all()
    )
    return [ObservationOut.model_validate(observation) for observation in observations]


@router.get("/{product_id}/metrics", response_model=list[MetricSnapshotOut])
def get_product_metrics(product_id: int, db: Session = Depends(get_db)) -> list[MetricSnapshotOut]:
    metrics = (
        db.query(MetricSnapshot)
        .filter(MetricSnapshot.product_id == product_id)
        .order_by(MetricSnapshot.snapshot_date.desc())
        .all()
    )
    return [MetricSnapshotOut.model_validate(metric) for metric in metrics]
