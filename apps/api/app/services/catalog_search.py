from __future__ import annotations

from decimal import Decimal
from typing import Literal, cast

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, selectinload

from app.models import MetricSnapshot, PriceObservation, Product, ProductAlias
from app.schemas.common import MetricSnapshotOut
from app.schemas.products import (
    ProductBrowseFacets,
    ProductBrowseResponse,
    ProductFacetCount,
    ProductListItem,
)

ProductBrowseSort = Literal[
    "updated_desc", "premium_desc", "freshness_desc", "confidence_desc", "name_asc"
]

CATEGORY_LABELS = {
    "trucker_hat": "trucker hats",
    "hoodie": "hoodies",
    "zip_up": "zip-ups",
    "long_sleeve": "long sleeves",
    "ring": "rings",
    "bracelet": "bracelets",
}

SOURCE_TYPE_LABELS = {
    "community_retail": "community retail",
    "curated_reseller": "curated resellers",
    "marketplace": "marketplaces",
    "sold_comp": "sold comps",
    "import": "imports",
}

MARKET_SIDE_LABELS = {
    "retail": "retail evidence",
    "ask": "ask evidence",
    "sold": "sold evidence",
}


def latest_metric_for_product(product: Product) -> MetricSnapshot | None:
    metrics = cast(list[MetricSnapshot], product.metrics)
    if not metrics:
        return None
    return max(metrics, key=lambda metric: metric.generated_at)


def build_product_list_item(product: Product) -> ProductListItem:
    latest_metric = latest_metric_for_product(product)
    return ProductListItem(
        **product.__dict__,
        latest_metric=MetricSnapshotOut.model_validate(latest_metric) if latest_metric else None,
    )


def _metric_decimal(metric_value: Decimal | None) -> Decimal:
    return metric_value if metric_value is not None else Decimal("-1")


def _filter_products_by_min_confidence(
    products: list[Product], min_confidence: Decimal | None
) -> list[Product]:
    if min_confidence is None:
        return products
    return [
        product
        for product in products
        if (latest_metric := latest_metric_for_product(product)) is not None
        and latest_metric.confidence_score is not None
        and latest_metric.confidence_score >= min_confidence
    ]


def _load_catalog_products(
    db: Session,
    *,
    query: str | None = None,
    categories: list[str] | None = None,
    source_types: list[str] | None = None,
    market_sides: list[str] | None = None,
) -> list[Product]:
    rows = db.query(Product).options(
        selectinload(Product.metrics), selectinload(Product.observations)
    )

    if query:
        rows = rows.outerjoin(ProductAlias, ProductAlias.product_id == Product.id).filter(
            or_(
                Product.canonical_name.ilike(f"%{query}%"),
                Product.slug.ilike(f"%{query}%"),
                ProductAlias.alias_text.ilike(f"%{query}%"),
            )
        )

    if categories:
        rows = rows.filter(Product.category.in_(categories))

    if source_types:
        rows = rows.filter(
            Product.observations.any(
                and_(
                    PriceObservation.status == "active",
                    PriceObservation.source_type_snapshot.in_(source_types),
                )
            )
        )

    if market_sides:
        rows = rows.filter(
            Product.observations.any(
                and_(
                    PriceObservation.status == "active",
                    PriceObservation.market_side.in_(market_sides),
                )
            )
        )

    return rows.distinct().all()


def _sort_product_items(
    items: list[ProductListItem], sort: ProductBrowseSort
) -> list[ProductListItem]:
    if sort == "name_asc":
        return sorted(items, key=lambda item: (item.canonical_name.lower(), item.id))
    if sort == "premium_desc":
        return sorted(
            items,
            key=lambda item: (
                _metric_decimal(
                    item.latest_metric.premium_vs_retail_pct if item.latest_metric else None
                ),
                item.updated_at,
                item.canonical_name.lower(),
            ),
            reverse=True,
        )
    if sort == "freshness_desc":
        return sorted(
            items,
            key=lambda item: (
                _metric_decimal(item.latest_metric.freshness_score if item.latest_metric else None),
                item.updated_at,
                item.canonical_name.lower(),
            ),
            reverse=True,
        )
    if sort == "confidence_desc":
        return sorted(
            items,
            key=lambda item: (
                _metric_decimal(
                    item.latest_metric.confidence_score if item.latest_metric else None
                ),
                item.updated_at,
                item.canonical_name.lower(),
            ),
            reverse=True,
        )
    return sorted(
        items, key=lambda item: (item.updated_at, item.canonical_name.lower()), reverse=True
    )


def _build_facet_counts(counts: dict[str, int], labels: dict[str, str]) -> list[ProductFacetCount]:
    ordered_keys = list(labels.keys())
    facet_items = [
        ProductFacetCount(
            key=key, label=labels.get(key, key.replace("_", " ")), count=counts.get(key, 0)
        )
        for key in ordered_keys
        if counts.get(key, 0) > 0 or key in counts
    ]
    return [item for item in facet_items if item.count > 0]


def _active_source_types(product: Product) -> set[str]:
    return {
        observation.source_type_snapshot
        for observation in product.observations
        if observation.status == "active"
    }


def _active_market_sides(product: Product) -> set[str]:
    return {
        observation.market_side
        for observation in product.observations
        if observation.status == "active"
    }


def _count_category_facets(products: list[Product]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for product in products:
        counts[product.category] = counts.get(product.category, 0) + 1
    return counts


def _count_source_type_facets(products: list[Product]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for product in products:
        for source_type in _active_source_types(product):
            counts[source_type] = counts.get(source_type, 0) + 1
    return counts


def _count_market_side_facets(products: list[Product]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for product in products:
        for market_side in _active_market_sides(product):
            counts[market_side] = counts.get(market_side, 0) + 1
    return counts


def _sorted_filtered_products(
    db: Session,
    *,
    query: str | None = None,
    categories: list[str] | None = None,
    source_types: list[str] | None = None,
    market_sides: list[str] | None = None,
    min_confidence: Decimal | None = None,
    sort: ProductBrowseSort = "updated_desc",
) -> list[Product]:
    products = _load_catalog_products(
        db,
        query=query,
        categories=categories,
        source_types=source_types,
        market_sides=market_sides,
    )
    filtered_products = _filter_products_by_min_confidence(products, min_confidence)
    sorted_items = _sort_product_items(
        [build_product_list_item(product) for product in filtered_products], sort
    )
    product_by_id = {product.id: product for product in filtered_products}
    return [product_by_id[item.id] for item in sorted_items]


def query_catalog_products(
    db: Session,
    *,
    query: str | None = None,
    categories: list[str] | None = None,
    source_types: list[str] | None = None,
    market_sides: list[str] | None = None,
    min_confidence: Decimal | None = None,
    sort: ProductBrowseSort = "updated_desc",
    limit: int = 50,
    offset: int = 0,
) -> list[ProductListItem]:
    products = _sorted_filtered_products(
        db,
        query=query,
        categories=categories,
        source_types=source_types,
        market_sides=market_sides,
        min_confidence=min_confidence,
        sort=sort,
    )
    return [build_product_list_item(product) for product in products[offset : offset + limit]]


def browse_catalog_products(
    db: Session,
    *,
    query: str | None = None,
    categories: list[str] | None = None,
    source_types: list[str] | None = None,
    market_sides: list[str] | None = None,
    min_confidence: Decimal | None = None,
    sort: ProductBrowseSort = "updated_desc",
    limit: int = 24,
    offset: int = 0,
) -> ProductBrowseResponse:
    products = _sorted_filtered_products(
        db,
        query=query,
        categories=categories,
        source_types=source_types,
        market_sides=market_sides,
        min_confidence=min_confidence,
        sort=sort,
    )
    total = len(products)
    items = [build_product_list_item(product) for product in products[offset : offset + limit]]

    category_products = _filter_products_by_min_confidence(
        _load_catalog_products(
            db,
            query=query,
            source_types=source_types,
            market_sides=market_sides,
        ),
        min_confidence,
    )
    source_type_products = _filter_products_by_min_confidence(
        _load_catalog_products(
            db,
            query=query,
            categories=categories,
            market_sides=market_sides,
        ),
        min_confidence,
    )
    market_side_products = _filter_products_by_min_confidence(
        _load_catalog_products(
            db,
            query=query,
            categories=categories,
            source_types=source_types,
        ),
        min_confidence,
    )

    facets = ProductBrowseFacets(
        categories=_build_facet_counts(_count_category_facets(category_products), CATEGORY_LABELS),
        source_types=_build_facet_counts(
            _count_source_type_facets(source_type_products), SOURCE_TYPE_LABELS
        ),
        market_sides=_build_facet_counts(
            _count_market_side_facets(market_side_products), MARKET_SIDE_LABELS
        ),
    )
    return ProductBrowseResponse(
        total=total,
        limit=limit,
        offset=offset,
        has_next_page=offset + len(items) < total,
        items=items,
        facets=facets,
    )


def search_catalog_products(db: Session, query: str, limit: int = 20) -> list[ProductListItem]:
    return query_catalog_products(db, query=query, sort="name_asc", limit=limit)
