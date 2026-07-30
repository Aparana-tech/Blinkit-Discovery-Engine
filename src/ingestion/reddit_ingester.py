import requests
import hashlib
import time
from typing import List, Dict, Any
from datetime import datetime
import logging
from .base_ingester import BaseIngester

logger = logging.getLogger(__name__)

class RedditIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="reddit")
        app_config = self.config.get('ingestion', {}).get('reddit', {})
        self.subreddits = app_config.get('subreddits', ['blinkit', 'india'])

    def _fetch_from_json(self, sub: str) -> Dict[str, Any]:
        """Strategy 1: Reddit .json search"""
        logger.info(f"Strategy 1: Fetching recent posts from r/{sub} via .json endpoint")
        posts = {}
        headers = {'User-Agent': 'BlinkitDiscoveryEngine/0.1'}
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q=blinkit&restrict_sr=on&sort=new&limit=100"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                children = data.get('data', {}).get('children', [])
                for child in children:
                    item = child.get('data', {})
                    item_id = item.get('id')
                    if item_id:
                        posts[item_id] = item
        except Exception as e:
            logger.warning(f"Error in .json strategy for r/{sub}: {e}")
        return posts

    def _fetch_from_mirrors(self, sub: str) -> Dict[str, Any]:
        """Strategy 2: Arctic Shift / PullPush mirrors for historical posts and comments"""
        logger.info(f"Strategy 2: Fetching posts/comments from r/{sub} via Mirrors")
        posts = {}
        
        # 1. Fetch Posts
        arctic_url = f"https://api.arctic-shift.photon-reddit.com/api/posts/search?subreddit={sub}&title=blinkit&limit=100"
        pullpush_url = f"https://api.pullpush.io/reddit/search/submission/?q=blinkit&subreddit={sub}&size=100"
        
        mirror_posts = self._robust_mirror_fetch(arctic_url, pullpush_url)
        
        for item in mirror_posts:
            item_id = item.get('id')
            if item_id:
                posts[item_id] = item
                # 2. Fetch Comments for this post
                logger.info(f"Fetching comments for post {item_id}...")
                c_arctic = f"https://api.arctic-shift.photon-reddit.com/api/comments/search?link_id={item_id}&limit=50"
                c_pullpush = f"https://api.pullpush.io/reddit/search/comment/?link_id={item_id}&size=50"
                comments = self._robust_mirror_fetch(c_arctic, c_pullpush)
                for c in comments:
                    c_id = c.get('id')
                    if c_id:
                        posts[f"comment_{c_id}"] = c
                        
                time.sleep(1) # Be nice to volunteer servers to avoid rate limits
                
        return posts

    def _robust_mirror_fetch(self, arctic_url: str, pullpush_url: str) -> List[Dict]:
        """Implements the mutual fallback mechanism between Arctic Shift and PullPush"""
        try:
            resp = requests.get(arctic_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('data', [])
            else:
                logger.warning(f"Arctic Shift returned {resp.status_code}. Falling back to PullPush.")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Arctic Shift timeout/error: {e}. Falling back to PullPush.")
            
        try:
            resp = requests.get(pullpush_url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('data', [])
        except requests.exceptions.RequestException as e:
            logger.warning(f"PullPush timeout/error: {e}.")
            
        return []

    def fetch(self) -> Any:
        all_items = {}
        for sub in self.subreddits:
            # 1. Native JSON Strategy
            json_posts = self._fetch_from_json(sub)
            all_items.update(json_posts)
            
            # 2. Mirror Strategy
            mirror_posts = self._fetch_from_mirrors(sub)
            # This implicitly deduplicates because we use dict updates keyed by ID!
            all_items.update(mirror_posts)
            
        return list(all_items.values())

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for item in raw_data:
            try:
                # Handle both posts (title+body) and comments (body only)
                review_id = f"reddit_{item.get('id', '')}"
                
                title = item.get('title', '')
                body = item.get('selftext', item.get('body', ''))
                text = f"{title} \n {body}".strip()
                
                author_name = item.get("author", "Unknown")
                created_utc = item.get("created_utc")
                
                if not review_id or not text or text == "[deleted]" or text == "[removed]":
                    continue

                author_hash = hashlib.sha256(author_name.encode()).hexdigest()
                date_str = ""
                if created_utc:
                    date_str = datetime.fromtimestamp(created_utc).strftime("%Y-%m-%d")

                normalized.append({
                    "platform": "reddit",
                    "review_id": review_id,
                    "rating": None, 
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
