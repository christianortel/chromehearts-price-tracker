from app.models import PriceObservation, Product
from app.services.adapters.ebay import EbayAdapter
from app.services.etl.pipeline import persist_observations
from sqlalchemy.orm import Session


def test_persist_observations_uses_matcher_for_auto_match(db_session: Session) -> None:
    product = db_session.query(Product).filter(Product.category == "ring").first()
    assert product is not None

    adapter = EbayAdapter()
    items = adapter.parse_listing_page(
        """
        <li class="s-item">
          <a class="s-item__link" href="https://www.ebay.com/itm/forever-ring-1">
            <span class="s-item__title">Chrome Hearts Forever Ring</span>
          </a>
          <span class="s-item__price">$895.00</span>
        </li>
        """
    )
    observations = adapter.to_observations(items)
    persisted = persist_observations(db_session, observations)
    db_session.commit()

    created = (
        db_session.query(PriceObservation).filter(PriceObservation.id == persisted[0].id).one()
    )
    assert created.product_id == product.id
    assert created.market_side == "ask"
