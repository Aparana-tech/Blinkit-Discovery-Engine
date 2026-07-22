import pytest
from src.processing.pii_scrubber import PIIScrubber
from src.processing.text_cleaner import TextCleaner

def test_pii_scrubber():
    scrubber = PIIScrubber()
    
    # Test Phone
    text = "Call me at +919876543210 regarding the order"
    assert scrubber.scrub_text(text) == "Call me at [PHONE_REMOVED] regarding the order"
    
    # Test Email
    text = "My email is john.doe@gmail.com"
    assert scrubber.scrub_text(text) == "My email is [EMAIL_REMOVED]"
    
    # Test UPI
    text = "I paid via aparna@okhdfcbank"
    assert scrubber.scrub_text(text) == "I paid via [UPI_REMOVED]"

def test_text_cleaner():
    cleaner = TextCleaner()
    
    # Test URL removal
    text = "Look at this https://google.com it is cool"
    assert cleaner.clean_text(text) == "Look at this it is cool"
    
    # Test whitespace
    text = "Too    much   space"
    assert cleaner.clean_text(text) == "Too much space"
    
    # Test validation
    assert not cleaner.is_valid_review("ok") # Too short
    assert cleaner.is_valid_review("this is a good app") # Valid
