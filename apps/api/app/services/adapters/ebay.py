from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.services.adapters.base import BaseSourceAdapter, DiscoveredItem
from app.services.etl.normalized import NormalizedObservation


class EbayAdapter(BaseSourceAdapter):
    source_name = "ebay"
    source_type = "marketplace"
    market_side = "ask"
    base_url = "https://www.ebay.com"

    def build_discovery_url(self, query: str) -> str:
        return f"{self.base_url}/sch/i.html?_nkw={quote_plus(query)}"

    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[DiscoveredItem] = []
        for node in soup.select("li.s-item"):
            title_node = node.select_one(".s-item__title")
            price_node = node.select_one(".s-item__price")
            link_node = node.select_one(".s-item__link")
            if not title_node or not price_node or not link_node:
                continue
            href = link_node.get("href")
            title = title_node.get_text(" ", strip=True)
            if not href or title.lower() == "shop on ebay":
                continue
            source_item_id = href.rstrip("/").split("/")[-1].split("?")[0]
            condition_node = node.select_one(".SECONDARY_INFO")
            shipping_node = node.select_one(".s-item__shipping")
            location_node = node.select_one(".s-item__location")
            items.append(
                DiscoveredItem(
                    source_item_id=source_item_id,
                    url=href,
                    title=title,
                    metadata={
                        "price_text": price_node.get_text(" ", strip=True),
                        "condition": condition_node.get_text(" ", strip=True) if condition_node else None,
                        "shipping_text": shipping_node.get_text(" ", strip=True) if shipping_node else None,
                        "location_text": location_node.get_text(" ", strip=True) if location_node else None,
                    },
                )
            )
        return items

    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        price_text = item.metadata["price_text"].replace("$", "").replace(",", "")
        price_amount = Decimal(price_text.split(" ")[0].split("to")[0].strip())
        shipping_amount = None
        shipping_text = item.metadata.get("shipping_text")
        if shipping_text and "$" in shipping_text:
            shipping_amount = Decimal(shipping_text.replace("$", "").split(" ")[0].replace(",", ""))
        normalized_title = self._normalize_title(item.title)
        observed_at = datetime.now(UTC)
        return NormalizedObservation(
            source_name=self.source_name,
            source_type=self.source_type,
            source_item_id=item.source_item_id,
            source_url=item.url,
            raw_title=item.title,
            normalized_title=normalized_title,
            market_side=self.market_side,
            seller_or_store="eBay seller",
            location_text=item.metadata.get("location_text"),
            condition=item.metadata.get("condition"),
            size_text=None,
            currency="USD",
            price_amount=price_amount,
            shipping_amount=shipping_amount,
            observed_at=observed_at,
            proof_type="listing",
            raw_payload=item.metadata,
            extraction_confidence=Decimal("0.820"),
            price_confidence=Decimal("0.620"),
            duplicate_group_key=self._build_duplicate_key(
                normalized_title,
                price_amount,
                observed_at.date().isoformat(),
            ),
        )

