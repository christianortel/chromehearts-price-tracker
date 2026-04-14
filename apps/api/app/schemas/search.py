from app.schemas.products import ProductListItem
from pydantic import BaseModel


class SearchResponse(BaseModel):
    query: str
    total: int
    items: list[ProductListItem]
