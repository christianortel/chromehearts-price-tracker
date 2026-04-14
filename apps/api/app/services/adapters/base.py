from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx

from app.services.etl.normalized import NormalizedObservation
from app.services.normalization import build_duplicate_group_key, normalize_text


@dataclass
class DiscoveredItem:
    source_item_id: str
    url: str
    title: str
    metadata: dict[str, Any]


class BaseSourceAdapter(ABC):
    source_name: str
    source_type: str
    market_side: str
    base_url: str

    def __init__(self, *, timeout: float = 20.0) -> None:
        self.timeout = timeout

    async def fetch_text(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            response = await client.get(url, headers={"user-agent": "CHPI-MVP/0.1"})
            response.raise_for_status()
            return response.text

    @abstractmethod
    def build_discovery_url(self, query: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def parse_listing_page(self, html: str) -> list[DiscoveredItem]:
        raise NotImplementedError

    @abstractmethod
    def normalize_item(self, item: DiscoveredItem) -> NormalizedObservation:
        raise NotImplementedError

    def to_observations(self, items: list[DiscoveredItem]) -> list[NormalizedObservation]:
        return [self.normalize_item(item) for item in items]

    def _build_duplicate_key(self, normalized_title: str, price_amount: Decimal, observed_at: str) -> str:
        return build_duplicate_group_key(
            self.source_name,
            normalized_title,
            f"{price_amount:.2f}",
            observed_at,
        )

    def _normalize_title(self, title: str) -> str:
        return normalize_text(title)

