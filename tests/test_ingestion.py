import pytest
from pathlib import Path
from src.ingestion.app_store import AppStoreIngester
from src.ingestion.play_store import PlayStoreIngester
from src.ingestion.reddit_ingester import RedditIngester
from src.ingestion.support_log_ingester import SupportLogIngester

def test_ingesters_initialization():
    app_store = AppStoreIngester()
    play_store = PlayStoreIngester()
    reddit = RedditIngester()
    support = SupportLogIngester()
    
    assert app_store.source_name == "app_store"
    assert play_store.source_name == "play_store"
    assert reddit.source_name == "reddit"
    assert support.source_name == "support_logs"

def test_support_log_fetch_and_normalize():
    support = SupportLogIngester()
    raw = support.fetch()
    assert len(raw) > 0 # Should fetch the 2 mock rows
    
    normalized = support.normalize(raw)
    assert len(normalized) > 0
    assert normalized[0]["platform"] == "support_logs"
    assert "review_id" in normalized[0]
    assert "text" in normalized[0]
