from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models import Product, ProductAlias
from app.services.normalization import infer_category, normalize_text


@dataclass
class MatchCandidate:
    product_id: int
    product_name: str | None
    score: Decimal
    reason: str


@dataclass
class MatchCatalogEntry:
    product_id: int
    canonical_name: str
    normalized_canonical_name: str
    category: str
    material: str | None
    aliases: list[str]


AUTO_MATCH_THRESHOLD = Decimal("0.920")
REVIEW_THRESHOLD = Decimal("0.700")


def _score_text_similarity(a: str, b: str) -> Decimal:
    return Decimal(str(round(SequenceMatcher(a=a, b=b).ratio(), 3)))


def build_match_catalog(db: Session) -> list[MatchCatalogEntry]:
    products = db.query(Product).all()
    aliases = db.query(ProductAlias).all()

    alias_map: dict[int, list[str]] = {}
    for alias in aliases:
        alias_map.setdefault(alias.product_id, []).append(normalize_text(alias.alias_text))

    return [
        MatchCatalogEntry(
            product_id=product.id,
            canonical_name=product.canonical_name,
            normalized_canonical_name=normalize_text(product.canonical_name),
            category=product.category,
            material=product.material,
            aliases=alias_map.get(product.id, []),
        )
        for product in products
    ]


def rank_products_against_catalog(
    raw_title: str, catalog: list[MatchCatalogEntry]
) -> list[MatchCandidate]:
    normalized = normalize_text(raw_title)
    category_hint = infer_category(normalized)
    candidates: list[MatchCandidate] = []
    for product in catalog:
        base_score = _score_text_similarity(normalized, product.normalized_canonical_name)
        reasons = ["canonical similarity"]
        if category_hint and product.category == category_hint:
            base_score += Decimal("0.100")
            reasons.append("category hint")
        for alias_text in product.aliases:
            alias_score = _score_text_similarity(normalized, alias_text)
            if alias_score > base_score:
                base_score = alias_score + Decimal("0.050")
                reasons = ["alias similarity"]
        if product.material and normalize_text(product.material) in normalized:
            base_score += Decimal("0.050")
            reasons.append("material keyword")
        candidates.append(
            MatchCandidate(
                product_id=product.product_id,
                product_name=product.canonical_name,
                score=min(base_score, Decimal("0.999")),
                reason=", ".join(reasons),
            )
        )
    return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)


def rank_products(db: Session, raw_title: str) -> list[MatchCandidate]:
    return rank_products_against_catalog(raw_title, build_match_catalog(db))


def choose_match(candidates: Iterable[MatchCandidate]) -> MatchCandidate | None:
    ranked = list(candidates)
    if not ranked:
        return None
    top = ranked[0]
    if top.score >= AUTO_MATCH_THRESHOLD:
        return top
    return None
