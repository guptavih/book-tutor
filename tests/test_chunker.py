import pytest
from app.ingestion.chunker import structural_partition

def test_structural_partitioning():
    # A mock book with 2 chapters and some text
    mock_markdown = """# Chapter 1: The Drawing
Once upon a time, I saw a magnificent picture.
It was a boa constrictor eating an elephant.

# Chapter 2: The Sheep
So I lived my life alone, until a plane crash.
I asked the little prince to draw me a sheep.
"""
    
    units = structural_partition(mock_markdown)
    
    # 1. Assert we found 2 chapters
    assert len(units) == 2
    
    # 2. Assert titles are correct
    assert units[0]["title"] == "Chapter 1: The Drawing"
    assert units[1]["title"] == "Chapter 2: The Sheep"
    
    # 3. Assert text is correctly captured
    assert "boa constrictor" in units[0]["text"]
    assert "plane crash" in units[1]["text"]
    
    # 4. Assert exact character offsets are recorded
    assert units[0]["char_start"] < units[0]["char_end"]
    assert units[1]["char_start"] > units[0]["char_end"]
    
    # 5. Validation check: Ensure extracting by offsets gives the exact text
    assert mock_markdown[units[0]["char_start"]:units[0]["char_end"]] == units[0]["text"]

def test_no_headings_fallback():
    # A mock text without any # headings
    mock_text = "This is a book with no chapters. Just endless text."
    units = structural_partition(mock_text)
    
    assert len(units) == 1
    assert units[0]["title"] == "Full Text"
    assert units[0]["text"] == mock_text