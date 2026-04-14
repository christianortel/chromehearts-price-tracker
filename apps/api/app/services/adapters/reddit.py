from app.services.adapters.base import BaseSourceAdapter, DiscoveredItem
from app.services.etl.normalized import NormalizedObservation


class RedditAdapter(BaseSourceAdapter):
    source_name = "reddit"
    source_type = "community_retail"
    market_side = "retail"
    base_url = "https://www.reddit.com"

    def build_discovery_url(self, query: str) -> str:
        raise NotImplementedError(
            "Reddit adapter is intentionally disabled pending compliant access approval."
        )

    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        raise NotImplementedError("Reddit adapter is intentionally stubbed.")

    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        raise NotImplementedError("Reddit adapter is intentionally stubbed.")
