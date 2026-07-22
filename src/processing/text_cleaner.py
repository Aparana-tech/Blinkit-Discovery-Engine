import re
from typing import Dict, Any, List

class TextCleaner:
    """Normalizes text and filters out noise."""
    
    def __init__(self):
        # Remove URLs
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        # Remove excessive whitespace
        self.space_pattern = re.compile(r'\s+')

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove extra whitespace
        text = self.space_pattern.sub(' ', text).strip()
        
        return text

    def is_valid_review(self, text: str) -> bool:
        """Filters out reviews that are too short to be useful."""
        if not text:
            return False
            
        # Basic heuristic: Must have at least 3 words
        words = text.split()
        if len(words) < 3:
            return False
            
        return True

    def process_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cleans a batch of records and filters out invalid ones."""
        cleaned_records = []
        for record in records:
            cleaned = record.copy()
            if 'text' in cleaned and isinstance(cleaned['text'], str):
                cleaned['text'] = self.clean_text(cleaned['text'])
                
                # Only keep records that still have valid text after cleaning
                if self.is_valid_review(cleaned['text']):
                    cleaned_records.append(cleaned)
                    
        return cleaned_records
