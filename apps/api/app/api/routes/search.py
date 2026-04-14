from app.db.session import get_db
from app.schemas.search import SearchResponse
from app.services.catalog_search import search_catalog_products
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search_products(
    q: str = Query(min_length=1),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
) -> SearchResponse:
    items = search_catalog_products(db, q, limit=limit)
    return SearchResponse(query=q, total=len(items), items=items)
