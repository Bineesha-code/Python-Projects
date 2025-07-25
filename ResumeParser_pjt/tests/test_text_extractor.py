"""
Unit tests for text extractor
"""
import pytest
from backend.utils.text_extractor import TextExtractor


class TestTextExtractor:
    """Test cases for TextExtractor class"""
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        raw_text = "This   is    a\n\n\ntest   text\nwith   extra   spaces"
        expected = "This is a test text with extra spaces"
        
        cleaned = TextExtractor.clean_text(raw_text)
        assert cleaned == expected
    
    def test_clean_text_empty(self):
        """Test cleaning empty text"""
        assert TextExtractor.clean_text("") == ""
        assert TextExtractor.clean_text(None) == ""
    
    def test_clean_text_special_chars(self):
        """Test cleaning text with special characters"""
        raw_text = "Email: john@example.com Phone: (555) 123-4567"
        cleaned = TextExtractor.clean_text(raw_text)
        
        # Should preserve email and phone format
        assert "@" in cleaned
        assert "(" in cleaned
        assert ")" in cleaned
        assert "-" in cleaned


if __name__ == "__main__":
    pytest.main([__file__])
