from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from .domain import NewsDomain
from .schema import NewsResponse

router = APIRouter(
    prefix="/news",
    tags=["News"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=NewsResponse)
async def get_ai_news(
    days: int = Query(7, description="Number of days to look back for news"),
    limit: int = Query(10, description="Maximum number of articles to return"),
    force_refresh: Optional[bool] = Query(False, description="Force a refresh of the cache"),
    news_domain: NewsDomain = Depends(NewsDomain)
):
    """
    Get the latest AI news from various sources.
    """
    return await news_domain.get_ai_news(days=days, limit=limit, force_refresh=force_refresh)

