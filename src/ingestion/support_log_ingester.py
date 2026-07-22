import csv
import hashlib
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from .base_ingester import BaseIngester

class SupportLogIngester(BaseIngester):
    def __init__(self):
        super().__init__(source_name="support_logs")
        self.mock_file = Path("data/mock_support_logs.csv")
        self._create_mock_data_if_needed()

    def _create_mock_data_if_needed(self):
        """Creates a mock CSV file representing an internal Freshdesk/Zendesk export."""
        if not self.mock_file.exists():
            self.mock_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.mock_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["ticket_id", "customer_name", "phone", "issue_text", "created_at"])
                writer.writerow(["TKT-1001", "Aparna R.", "+919876543210", "I couldn't find dog food anywhere on the app. Is pet care removed?", "2026-07-01"])
                writer.writerow(["TKT-1002", "John Doe", "011-22334455", "Bought a phone charger but was worried about warranty. Needs better descriptions.", "2026-07-05"])

    def fetch(self) -> Any:
        rows = []
        if self.mock_file.exists():
            with open(self.mock_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        return rows

    def normalize(self, raw_data: Any) -> List[Dict[str, Any]]:
        normalized = []
        for row in raw_data:
            try:
                ticket_id = row.get("ticket_id", "")
                text = row.get("issue_text", "")
                # We simulate PII scrubbing at the boundary by discarding name/phone entirely 
                # and hashing a combination to create an anonymous author ID
                customer_name = row.get("customer_name", "Unknown")
                date_str = row.get("created_at", "")
                
                if not ticket_id or not text:
                    continue

                author_hash = hashlib.sha256(customer_name.encode()).hexdigest()

                normalized.append({
                    "platform": "support_logs",
                    "review_id": ticket_id,
                    "rating": None, # Support tickets don't have star ratings
                    "text": text,
                    "date": date_str,
                    "author_id_hash": author_hash
                })
            except Exception as e:
                self.logger.warning(f"Error parsing Support Log entry: {e}")
                continue

        return normalized

if __name__ == "__main__":
    ingester = SupportLogIngester()
    ingester.run()
