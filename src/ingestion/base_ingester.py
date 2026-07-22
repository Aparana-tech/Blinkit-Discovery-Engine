import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseIngester(ABC):
    """
    Abstract base class for all data ingesters.
    Enforces a standard pipeline: fetch() -> normalize() -> save()
    """
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.config = self._load_config()
        self.output_dir = Path(self.config.get('data_paths', {}).get('raw', 'data/raw'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        config_path = Path("config/settings.yaml")
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        return {}

    @abstractmethod
    def fetch(self) -> Any:
        """Fetch raw data from the source."""
        pass

    @abstractmethod
    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        """
        Convert raw data into the standard JSON schema.
        Required fields per item:
        - platform: str
        - review_id: str
        - rating: int (or None)
        - text: str
        - date: str (YYYY-MM-DD)
        - author_id_hash: str (or None)
        """
        pass

    def save(self, normalized_data: List[Dict[str, Any]]) -> str:
        """Save normalized data to JSON."""
        if not normalized_data:
            logger.warning(f"[{self.source_name}] No data to save.")
            return ""

        # Deduplicate by review_id
        unique_data = {item['review_id']: item for item in normalized_data}.values()
        final_list = list(unique_data)

        timestamp = datetime.now().strftime('%Y-%m')
        filename = f"{self.source_name}_{timestamp}.json"
        filepath = self.output_dir / filename

        # If file exists, merge and deduplicate
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing_data = json.load(f)
            merged = {item['review_id']: item for item in existing_data}
            for item in final_list:
                merged[item['review_id']] = item
            final_list = list(merged.values())

        with open(filepath, 'w') as f:
            json.dump(final_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[{self.source_name}] Saved {len(final_list)} unique records to {filepath}")
        return str(filepath)

    def run(self):
        """Execute the ingestion pipeline."""
        logger.info(f"[{self.source_name}] Starting ingestion...")
        try:
            raw = self.fetch()
            normalized = self.normalize(raw)
            filepath = self.save(normalized)
            logger.info(f"[{self.source_name}] Ingestion complete.")
            return filepath
        except Exception as e:
            logger.error(f"[{self.source_name}] Ingestion failed: {str(e)}")
            raise
