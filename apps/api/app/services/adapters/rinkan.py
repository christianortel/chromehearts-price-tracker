from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.services.adapters.base import BaseSourceAdapter, DiscoveredItem
from app.services.etl.normalized import NormalizedObservation


class RinkanAdapter(BaseSourceAdapter):
    source_name = "rinkan"
    source_type = "curated_reseller"
    market_side = "ask"
    base_url = "https://rinkan-online.com"

    def build_discovery_url(self, query: str) -> str:
        return f"{self.base_url}/search?keyword={quote_plus(query)}"

    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        soup = BeautifulSoup(html, "html.parser")
        items: list[DiscoveredItem] = []
        for node in soup.select("[data-item-id]"):
            item_id = node.get("data-item-id")
            title_node = node.select_one(".item-name, .product-name")
            price_node = node.select_one(".price, .item-price")
            link_node = node.select_one("a[href]")
            condition_node = node.select_one(".condition")
            if not item_id or not title_node or not price_node or not link_node:
                continue
            href = link_node.get("href")
            if not href:
                continue
            if href.startswith("/"):
                href = f"{self.base_url}{href}"
            items.append(
                DiscoveredItem(
                    source_item_id=item_id,
                    url=href,
                    title=title_node.get_text(" ", strip=True),
                    metadata={
                        "price_text": price_node.get_text(" ", strip=True),
                        "condition": condition_node.get_text(" ", strip=True)
                        if condition_node
                        else None,
                        "location_text": "Japan",
                    },
                )
            )
        return items

    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        price_text = item.metadata["price_text"]
        price_text = price_text.replace("\u00a5", "").replace("\u00c2\u00a5", "")
        clean = price_text.replace("¥", "").replace(",", "").replace("JPY", "").strip()
        yen_amount = Decimal(clean.split(" ")[0])
        usd_amount = (yen_amount / Decimal("150")).quantize(Decimal("0.01"))
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
            seller_or_store="Rinkan",
            location_text=item.metadata.get("location_text"),
            condition=item.metadata.get("condition"),
            currency="USD",
            price_amount=usd_amount,
            observed_at=observed_at,
            proof_type="listing",
            raw_payload={
                **item.metadata,
                "original_currency": "JPY",
                "original_price": str(yen_amount),
            },
            extraction_confidence=Decimal("0.880"),
            price_confidence=Decimal("0.760"),
            duplicate_group_key=self._build_duplicate_key(
                normalized_title,
                usd_amount,
                observed_at.date().isoformat(),
            ),
        )
