from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NewsArticle(BaseModel):
    title: str
    content: str
    url: str
    source: str
    published_at: datetime
    image_url: Optional[str] = None
    author: Optional[str] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total_count: int
    last_updated: datetime

    class Config:
        orm_mode = True
