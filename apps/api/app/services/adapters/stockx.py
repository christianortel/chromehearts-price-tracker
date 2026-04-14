from app.services.adapters.base import BaseSourceAdapter, DiscoveredItem
from app.services.etl.normalized import NormalizedObservation


class StockxAdapter(BaseSourceAdapter):
    source_name = "stockx"
    source_type = "sold_comp"
    market_side = "sold"
    base_url = "https://stockx.com"

    def build_discovery_url(self, query: str) -> str:
        raise NotImplementedError("StockX adapter remains disabled pending coverage feasibility.")

    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        raise NotImplementedError("StockX adapter remains disabled pending coverage feasibility.")

    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        raise NotImplementedError("StockX adapter remains disabled pending coverage feasibility.")

