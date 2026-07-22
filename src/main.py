import logging
import sys
from pathlib import Path

# Setup logging for the master orchestrator
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("BlinkitDiscoveryEngine")

from src.ingestion.app_store import AppStoreIngester
from src.ingestion.play_store import PlayStoreIngester
from src.ingestion.reddit_ingester import RedditIngester
from src.ingestion.support_log_ingester import SupportLogIngester
from src.processing.pipeline import NLP_Pipeline

def run_ingestion():
    """Runs all data scrapers to collect fresh data."""
    logger.info("========== STEP 1: DATA INGESTION ==========")
    
    ingesters = [
        AppStoreIngester(),
        PlayStoreIngester(),
        RedditIngester(),
        SupportLogIngester()
    ]
    
    for ingester in ingesters:
        try:
            logger.info(f"Running {ingester.source_name} ingester...")
            ingester.run()
        except Exception as e:
            logger.error(f"Failed to ingest from {ingester.source_name}: {e}")
            
    logger.info("========== INGESTION COMPLETE ==========\n")

def run_processing():
    """Runs the AI pipeline to clean, cluster, label, and generate the report."""
    logger.info("========== STEP 2: AI PROCESSING & DELIVERY ==========")
    try:
        pipeline = NLP_Pipeline()
        pipeline.run()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
    logger.info("========== PROCESSING COMPLETE ==========\n")

def main():
    logger.info("🚀 Starting Blinkit Discovery Engine Orchestrator...")
    
    # Ensure directories exist
    for d in ["data/raw", "data/processed", "data/insights"]:
        Path(d).mkdir(parents=True, exist_ok=True)
        
    run_ingestion()
    run_processing()
    
    logger.info("✅ Engine execution finished successfully. Insights are ready.")

if __name__ == "__main__":
    main()
