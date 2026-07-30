import os
import requests
import hashlib
import logging
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from .base_ingester import BaseIngester

load_dotenv()
logger = logging.getLogger(__name__)

class AppStoreIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="app_store")
        app_config = self.config.get('ingestion', {}).get('app_store', {})
        self.app_id = app_config.get('app_id', '1406859344') # Blinkit ID
        self.country = app_config.get('country', 'in')
        self.api_key = os.getenv("SERPAPI_KEY")

    def fetch(self) -> Any:
        if not self.api_key:
            logger.error("No SERPAPI_KEY found in .env. Skipping Apple App Store ingestion.")
            return []
            
        all_reviews = []
        # SerpApi returns 10 reviews per page. We fetch 10 pages = 100 reviews.
        # This keeps the usage low (10 API credits out of 250) while getting enough data to prove it works.
        pages_to_fetch = 10 
        
        for page in range(1, pages_to_fetch + 1):
            url = f"https://serpapi.com/search.json?engine=apple_reviews&product_id={self.app_id}&country={self.country}&page={page}&sort=mostrecent&api_key={self.api_key}"
            try:
                logger.info(f"Fetching Apple App Store reviews page {page} via SerpApi...")
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    reviews = data.get("reviews", [])
                    if not reviews:
                        logger.info("No more reviews found on this page.")
                        break
                    all_reviews.extend(reviews)
                else:
                    logger.warning(f"SerpApi Error: {response.status_code} - {response.text}")
                    break
            except Exception as e:
                logger.warning(f"SerpApi request failed: {e}")
                break
                
        return all_reviews

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for review in raw_data:
            try:
                # SerpApi 'apple_reviews' format
                review_id = review.get('id', '')
                if not review_id:
                    continue
                    
                rating = review.get('rating', 0)
                text = f"{review.get('title', '')} \n {review.get('text', '')}".strip()
                author_name = review.get('author', {}).get('name', 'Unknown')
                date_str = review.get('date', datetime.now().strftime("%Y-%m-%d"))
                
                if not text:
                    continue

                author_hash = hashlib.sha256(author_name.encode()).hexdigest()

                normalized.append({
                    "platform": "app_store",
                    "review_id": f"apple_{review_id}",
                    "rating": rating,
                    "text": text,
                    "date": date_str, 
                    "author_id_hash": author_hash
                })
            except Exception as e:
                logger.warning(f"Error parsing Apple App Store entry: {e}")
                continue

        return normalized

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingester = AppStoreIngester()
    ingester.run()
