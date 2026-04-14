from pathlib import Path

from app.services.adapters.ebay import EbayAdapter
from app.services.adapters.rinkan import RinkanAdapter


def test_ebay_adapter_parses_and_normalizes_fixture() -> None:
    html = (Path(__file__).resolve().parents[1] / "fixtures" / "ebay_search.html").read_text(
        encoding="utf-8"
    )
    adapter = EbayAdapter()
    items = adapter.parse_listing_page(html)
    assert len(items) == 1
    observation = adapter.normalize_item(items[0])
    assert observation.source_name == "ebay"
    assert observation.market_side == "ask"
    assert observation.price_amount == 795
    assert observation.shipping_amount == 18


def test_rinkan_adapter_parses_and_normalizes_fixture() -> None:
    html = (Path(__file__).resolve().parents[1] / "fixtures" / "rinkan_search.html").read_text(
        encoding="utf-8"
    )
    adapter = RinkanAdapter()
    items = adapter.parse_listing_page(html)
    assert len(items) == 1
    observation = adapter.normalize_item(items[0])
    assert observation.source_name == "rinkan"
    assert observation.market_side == "ask"
    assert observation.raw_payload["original_currency"] == "JPY"
    assert observation.price_amount > 500
