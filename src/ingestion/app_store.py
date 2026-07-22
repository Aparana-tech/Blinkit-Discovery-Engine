import requests
import hashlib
from typing import List, Dict, Any
from .base_ingester import BaseIngester

class AppStoreIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="app_store")
        # Default to Blinkit iOS app ID if not in config
        app_config = self.config.get('ingestion', {}).get('app_store', {})
        self.app_id = app_config.get('app_id', '1406859344')
        self.country = app_config.get('country', 'in')

    def fetch(self) -> Any:
        # iTunes RSS feed for customer reviews
        url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/id={self.app_id}/sortBy=mostRecent/json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        feed = raw_data.get("feed", {})
        entries = feed.get("entry", [])
        
        # The first entry in the RSS feed is usually metadata about the app itself
        if entries and not entries[0].get("author"):
            entries = entries[1:]

        for entry in entries:
            try:
                review_id = entry.get("id", {}).get("label", "")
                rating = int(entry.get("im:rating", {}).get("label", 0))
                text = entry.get("content", {}).get("label", "")
                # Apple RSS doesn't give a standard date field easily, so we use author info for hashing
                author_name = entry.get("author", {}).get("name", {}).get("label", "Unknown")
                
                if not review_id or not text:
                    continue

                author_hash = hashlib.sha256(author_name.encode()).hexdigest()

                normalized.append({
                    "platform": "app_store",
                    "review_id": review_id,
                    "rating": rating,
                    "text": text,
                    # We default to today's date since RSS gives most recent
                    "date": datetime.now().strftime("%Y-%m-%d"), 
                    "author_id_hash": author_hash
                })
            except Exception as e:
                self.logger.warning(f"Error parsing App Store entry: {e}")
                continue

        return normalized

if __name__ == "__main__":
    from datetime import datetime # Local import for standalone run
    ingester = AppStoreIngester()
    ingester.run()
