import requests
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from .base_ingester import BaseIngester

class RedditIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="reddit")
        app_config = self.config.get('ingestion', {}).get('reddit', {})
        self.subreddits = app_config.get('subreddits', ['blinkit', 'india'])

    def fetch(self) -> Any:
        import time
        all_posts = []
        headers = {'User-Agent': 'BlinkitDiscoveryEngine/0.1'}
        max_posts_per_sub = 300
        
        for sub in self.subreddits:
            try:
                after_token = None
                posts_collected = 0
                
                while posts_collected < max_posts_per_sub:
                    # Use public JSON endpoint with pagination
                    url = f"https://www.reddit.com/r/{sub}/search.json?q=blinkit&restrict_sr=on&sort=new&limit=100"
                    if after_token:
                        url += f"&after={after_token}"
                        
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    children = data.get('data', {}).get('children', [])
                    if not children:
                        break # No more posts found
                        
                    for child in children:
                        all_posts.append(child.get('data', {}))
                        posts_collected += 1
                        
                    after_token = data.get('data', {}).get('after')
                    if not after_token or posts_collected >= max_posts_per_sub:
                        break # End of results
                        
                    # Sleep for 2 seconds to act like a human and avoid IP bans
                    self.logger.info(f"Sleeping 2s to prevent IP ban. Collected {posts_collected} so far from r/{sub}...")
                    time.sleep(2)
                    
            except Exception as e:
                self.logger.warning(f"Error fetching from r/{sub}: {e}")
                
        return all_posts

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for post in raw_data:
            try:
                review_id = f"reddit_{post.get('id', '')}"
                text = f"{post.get('title', '')} \n {post.get('selftext', '')}".strip()
                author_name = post.get("author", "Unknown")
                created_utc = post.get("created_utc")
                
                if not review_id or not text:
                    continue

                author_hash = hashlib.sha256(author_name.encode()).hexdigest()
                date_str = ""
                if created_utc:
                    date_str = datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d")

                normalized.append({
                    "platform": "reddit",
                    "review_id": review_id,
                    "rating": None, # Reddit posts don't have star ratings
                    "text": text,
                    "date": date_str,
                    "author_id_hash": author_hash
                })
            except Exception as e:
                self.logger.warning(f"Error parsing Reddit entry: {e}")
                continue

        return normalized

if __name__ == "__main__":
    ingester = RedditIngester()
    ingester.run()
