import feedparser
import datetime
import hashlib
from typing import List
from src.models import NewsItem
from src.utils.config_loader import get_config
from src.utils.logger import get_logger
from src.utils.state_manager import get_state_manager

logger = get_logger("NewsFetcher")

class NewsFetcher:
    def __init__(self):
        self.sources = get_config("news_sources.rss", [])
        self.state_manager = get_state_manager()

    def fetch_all(self) -> List[NewsItem]:
        all_news = []
        for source in self.sources:
            try:
                news_items = self.fetch_feed(source['url'], source['name'])
                all_news.extend(news_items)
            except Exception as e:
                logger.error(f"Error fetching {source['name']}: {e}")
        
        # Filter processed
        new_items = []
        for item in all_news:
            if not self.state_manager.is_news_processed(item.id):
                new_items.append(item)
                # We mark as processed AFTER analysis/action? 
                # Or mark now? If we mark now and crash, we lose it.
                # Better to return it, and let the main loop mark it after processing.
                # But to avoid re-fetching in next loop if main loop crashes, we need careful state handling.
                # For MVP: The main loop will retrieve these, process them, and then mark them processed.
                # So we just filter here.
        
        logger.info(f"Fetched {len(new_items)} new articles.")
        return new_items

    def fetch_feed(self, url: str, source_name: str) -> List[NewsItem]:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            # Create unique ID based on URL or title
            uid_str = entry.link if 'link' in entry else entry.title
            item_id = hashlib.md5(uid_str.encode('utf-8')).hexdigest()
            
            # Parse Date
            published = datetime.datetime.utcnow().isoformat()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.datetime(*entry.published_parsed[:6]).isoformat()
            
            # Content
            content = entry.summary if 'summary' in entry else entry.title
            
            item = NewsItem(
                id=item_id,
                source=source_name,
                title=entry.title,
                url=entry.link,
                published_at=published,
                content=content
            )
            items.append(item)
        return items

