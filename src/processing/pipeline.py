import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from src.processing.text_cleaner import TextCleaner
from src.processing.pii_scrubber import PIIScrubber
from src.processing.clusterer import ReviewClusterer
from src.processing.llm_labeler import LLMLabeler
from src.delivery.report_generator import ReportGenerator

# Load environment variables (GROQ_API_KEY)
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NLP_Pipeline:
    def __init__(self):
        self.cleaner = TextCleaner()
        self.scrubber = PIIScrubber()
        self.clusterer = ReviewClusterer()
        self.labeler = LLMLabeler()
        self.reporter = ReportGenerator()
        
        self.raw_dir = Path("data/raw")
        self.processed_dir = Path("data/processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def load_raw_data(self) -> List[Dict[str, Any]]:
        """Loads all JSON files in the raw data directory."""
        all_records = []
        if not self.raw_dir.exists():
            logger.error(f"Raw data directory {self.raw_dir} does not exist.")
            return all_records
            
        for file_path in self.raw_dir.glob("*.json"):
            logger.info(f"Loading {file_path.name}...")
            with open(file_path, "r") as f:
                data = json.load(f)
                all_records.extend(data)
                
        logger.info(f"Total raw records loaded: {len(all_records)}")
        return all_records

    def run(self):
        logger.info("=== Starting Phase 2: NLP Pipeline ===")
        
        # 1. Load Data
        records = self.load_raw_data()
        if not records:
            logger.warning("No data found to process.")
            return

        # 2. Clean Data (filter short reviews, remove URLs)
        cleaned_records = self.cleaner.process_records(records)
        logger.info(f"Records remaining after cleaning: {len(cleaned_records)}")

        # 3. PII Scrubbing
        scrubbed_records = [self.scrubber.scrub_record(r) for r in cleaned_records]
        logger.info("PII Scrubbing complete.")

        # 4. Clustering (Local Embeddings)
        logger.info("Starting Semantic Clustering...")
        clusters = self.clusterer.cluster_reviews(scrubbed_records)

        # 5. LLM Labeling
        logger.info("Starting LLM Theme Labeling...")
        final_insights = []
        for cluster_id, cluster_records in clusters.items():
            if cluster_id == -1:
                # Noise cluster, we can just save it without hitting LLM to save tokens
                final_insights.append({
                    "cluster_id": -1,
                    "theme_name": "Uncategorized Noise",
                    "pillar": "N/A",
                    "size": len(cluster_records),
                    "reviews": cluster_records
                })
                continue
                
            insight = self.labeler.label_cluster(cluster_id, cluster_records)
            final_insights.append(insight)

        # 6. Save Processed Output
        timestamp = datetime.now().strftime("%Y-%m")
        output_path = self.processed_dir / f"clusters_{timestamp}.json"
        
        with open(output_path, "w") as f:
            json.dump(final_insights, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved {len(final_insights)} themes to {output_path}")
        
        # 7. Generate Final Report
        logger.info("Generating Final One-Pager Report...")
        report_path = self.reporter.generate_report(final_insights, timestamp)
            
        logger.info(f"=== NLP Pipeline Complete. Report ready at {report_path} ===")

if __name__ == "__main__":
    pipeline = NLP_Pipeline()
    pipeline.run()
