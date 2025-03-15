from datetime import datetime, timedelta
import httpx
from typing import List, Optional
from fastapi import HTTPException, status
import feedparser
from .schema import NewsArticle, NewsResponse

class NewsRepository:
    def __init__(self):
        self.rss_feeds = {
            "venturebeat": "https://venturebeat.com/category/ai/feed/",
            "techcrunch": "https://techcrunch.com/tag/artificial-intelligence/feed/",
            "wired": "https://www.wired.com/feed/rss",
            "mit_tech_review": "https://www.technologyreview.com/feed/",
            "ai_news": "https://artificialintelligence-news.com/feed/"
        }
        self.cache_duration = timedelta(hours=1)
        self._last_fetch = None
        self._cached_news = None

    async def get_ai_news(
        self,
        days: int = 7,
        limit: int = 10,
        force_refresh: bool = False
    ) -> NewsResponse:
        """
        Fetch AI-related news from RSS feeds.

        Args:
            days (int): Number of days to look back for news
            limit (int): Maximum number of articles to return
            force_refresh (bool): Whether to force a refresh of cached data

        Returns:
            NewsResponse: Object containing the news articles and metadata
        """
        # Check cache if not forcing refresh
        if not force_refresh and self._cached_news and self._last_fetch:
            if datetime.now() - self._last_fetch < self.cache_duration:
                return self._cached_news

        try:
            articles = []
            cutoff_date = datetime.now() - timedelta(days=days)

            async with httpx.AsyncClient() as client:
                for source, feed_url in self.rss_feeds.items():
                    try:
                        response = await client.get(feed_url)
                        if response.status_code == 200:
                            feed = feedparser.parse(response.content)
                            
                            for entry in feed.entries:
                                try:
                                    # Parse the published date
                                    published_at = datetime(*entry.published_parsed[:6])
                                    
                                    # Skip if article is too old
                                    if published_at < cutoff_date:
                                        continue
                                        
                                    # Check if the article is AI-related
                                    title = entry.title.lower()
                                    description = entry.get('description', '').lower()
                                    ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network']
                                    
                                    if not any(keyword in title or keyword in description for keyword in ai_keywords):
                                        continue
                                    
                                    news_article = NewsArticle(
                                        title=entry.title,
                                        content=entry.get('description', entry.title),
                                        url=entry.link,
                                        source=source,
                                        published_at=published_at,
                                        image_url=entry.get('media_content', [{}])[0].get('url') if 'media_content' in entry else None,
                                        author=entry.get('author', None)
                                    )
                                    articles.append(news_article)
                                except (AttributeError, ValueError) as e:
                                    continue
                                    
                    except Exception as e:
                        continue

            # Sort articles by published date and limit the number
            articles.sort(key=lambda x: x.published_at, reverse=True)
            articles = articles[:limit]

            # Create response
            news_response = NewsResponse(
                articles=articles,
                total_count=len(articles),
                last_updated=datetime.now()
            )

            # Update cache
            self._cached_news = news_response
            self._last_fetch = datetime.now()

            return news_response

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
