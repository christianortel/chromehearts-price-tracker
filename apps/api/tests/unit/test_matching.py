from app.services.matching.engine import choose_match, rank_products
from sqlalchemy.orm import Session


def test_rank_products_prefers_alias_match(db_session: Session) -> None:
    candidates = rank_products(db_session, "CH Forever Ring")
    assert candidates
    assert candidates[0].score > 0.9


def test_choose_match_returns_none_below_threshold() -> None:
    assert choose_match([]) is None
