from app.services.adapters.base import BaseSourceAdapter
from app.services.adapters.ebay import EbayAdapter
from app.services.adapters.justin_reed import JustinReedAdapter
from app.services.adapters.reddit import RedditAdapter
from app.services.adapters.rinkan import RinkanAdapter
from app.services.adapters.stockx import StockxAdapter


def build_adapter_registry() -> dict[str, BaseSourceAdapter]:
    return {
        "ebay": EbayAdapter(),
        "rinkan": RinkanAdapter(),
        "reddit": RedditAdapter(),
        "justin_reed": JustinReedAdapter(),
        "stockx": StockxAdapter(),
    }

