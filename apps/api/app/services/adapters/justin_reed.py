from app.services.adapters.base import BaseSourceAdapter, DiscoveredItem
from app.services.etl.normalized import NormalizedObservation


class JustinReedAdapter(BaseSourceAdapter):
    source_name = "justin_reed"
    source_type = "curated_reseller"
    market_side = "ask"
    base_url = "https://www.justinreed.com"

    def build_discovery_url(self, query: str) -> str:
        raise NotImplementedError("Justin Reed adapter is stubbed until selectors are validated.")

    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        raise NotImplementedError("Justin Reed adapter is stubbed until selectors are validated.")

    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        raise NotImplementedError("Justin Reed adapter is stubbed until selectors are validated.")

