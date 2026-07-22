import re
from typing import Dict, Any

class PIIScrubber:
    """Removes sensitive personal data from text."""
    
    def __init__(self):
        # Regular expressions for common Indian PII
        self.phone_pattern = re.compile(r'(\+91[\-\s]?|0)?[6-9]\d{9}')
        self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.upi_pattern = re.compile(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}')

    def scrub_text(self, text: str) -> str:
        """Removes PII from a single string."""
        if not text:
            return ""
            
        # Replace matches with safe placeholders
        text = self.phone_pattern.sub('[PHONE_REMOVED]', text)
        text = self.email_pattern.sub('[EMAIL_REMOVED]', text)
        text = self.upi_pattern.sub('[UPI_REMOVED]', text)
        
        return text

    def scrub_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Scrubs the 'text' field of a data record."""
        scrubbed = record.copy()
        if 'text' in scrubbed and isinstance(scrubbed['text'], str):
            scrubbed['text'] = self.scrub_text(scrubbed['text'])
        return scrubbed
