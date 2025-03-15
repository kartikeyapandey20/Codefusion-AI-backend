from .repository import NewsRepository
from .schema import NewsResponse

class NewsDomain:
    def __init__(self):
        self.news_repository = NewsRepository()
    
    async def get_ai_news(self, days: int = 7, limit: int = 10, force_refresh: bool = False) -> NewsResponse:
        return await self.news_repository.get_ai_news(days, limit, force_refresh)   
    
