from pydantic import BaseModel

from app.schemas.products import ProductListItem


class SearchResponse(BaseModel):
    query: str
    total: int
    items: list[ProductListItem]

