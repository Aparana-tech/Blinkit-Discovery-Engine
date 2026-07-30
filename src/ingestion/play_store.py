import hashlib
from typing import List, Dict, Any
from google_play_scraper import reviews, Sort
from .base_ingester import BaseIngester

class PlayStoreIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="play_store")
        app_config = self.config.get('ingestion', {}).get('play_store', {})
        self.app_id = app_config.get('app_id', 'com.grofers.customerapp')

    def fetch(self) -> Any:
        # Fetch up to 1000 most recent reviews
        result, continuation_token = reviews(
            self.app_id,
            lang='en', 
            country='in', 
            sort=Sort.NEWEST, 
            count=3000
        )
        return result

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for review in raw_data:
            try:
                review_id = review.get("reviewId", "")
                rating = review.get("score", 0)
                text = review.get("content", "")
                date_obj = review.get("at")
                author_name = review.get("userName", "Unknown")
                
                if not review_id or not text:
                    continue

                author_hash = hashlib.sha256(author_name.encode()).hexdigest()
                
                date_str = ""
                if date_obj:
                    date_str = date_obj.strftime("%Y-%m-%d")

                normalized.append({
                    "platform": "play_store",
                    "review_id": review_id,
                    "rating": rating,
                    "text": text,
                    "date": date_str,
                    "author_id_hash": author_hash
                })
            except Exception as e:
                self.logger.warning(f"Error parsing Play Store entry: {e}")
                continue

        return normalized

if __name__ == "__main__":
    ingester = PlayStoreIngester()
    ingester.run()
