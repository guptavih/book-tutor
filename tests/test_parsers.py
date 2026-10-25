import pytest
from app.ingestion.parsers import parse_document, normalize_text

def test_parse_document_fallback():
    # Test parsing a plain text file (uses fallback)
    text = parse_document("tests/data/sample.txt")
    assert "This is a test" in text

def test_normalize_text_and_offsets():
    raw = "Hello world-\nThis is a test.\r\n\r\nNew line.\ufeff"
    
    normalized, offset_map = normalize_text(raw)
    
    # 1. Check that hyphenation is joined and whitespace is collapsed
    assert normalized == "Hello worldThis is a test. New line."
    
    # 2. Check that the offset map matches the length of the normalized string
    assert len(normalized) == len(offset_map)
    
    # 3. Verify the first character maps correctly
    original_idx, normalized_idx = offset_map[0]
    assert raw[original_idx] == 'H'
    assert normalized[normalized_idx] == 'H'