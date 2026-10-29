import re
from typing import List, Dict

def structural_partition(markdown_text: str) -> List[Dict]:
    """Splits markdown text by Level 1 headings."""
    heading_pattern = re.compile(r'^#\s+(.+)$', re.MULTILINE)
    matches = list(heading_pattern.finditer(markdown_text))
    
    if not matches:
        return [{
            "title": "Full Text",
            "text": markdown_text,
            "char_start": 0,
            "char_end": len(markdown_text)
        }]
        
    units = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start_idx = match.start()
        
        if i + 1 < len(matches):
            end_idx = matches[i+1].start()
        else:
            end_idx = len(markdown_text)
            
        unit_text = markdown_text[start_idx:end_idx].strip()
        actual_start = markdown_text.find(unit_text, start_idx)
        actual_end = actual_start + len(unit_text)
        
        units.append({
            "title": title,
            "text": unit_text,
            "char_start": actual_start,
            "char_end": actual_end
        })
        
    validate_partitioning(units, len(markdown_text))
    return units

def validate_partitioning(units: List[Dict], original_length: int):
    """Validates that chunks don't overlap."""
    for i in range(len(units) - 1):
        if units[i]["char_end"] > units[i+1]["char_start"]:
            raise ValueError(f"Overlap detected between '{units[i]['title']}' and '{units[i+1]['title']}'")
    if units[-1]["char_end"] > original_length:
        raise ValueError("Partitioning extends beyond original length.")

def semantic_size_enforcement(units: List[Dict]) -> List[Dict]:
    """
    Ensures no unit is larger than 5,000 words by splitting it.
    """
    MAX_WORDS = 5000
    processed_units = []
    
    for unit in units:
        word_count = len(unit["text"].split())
        
        if word_count > MAX_WORDS:
            text = unit["text"]
            half_idx = len(text) // 2
            split_idx = text.find(' ', half_idx)
            if split_idx == -1:
                split_idx = half_idx
                
            unit_1_text = text[:split_idx].strip()
            unit_2_text = text[split_idx:].strip()
            
            processed_units.append({
                "title": unit["title"] + " (Part 1)",
                "text": unit_1_text,
                "char_start": unit["char_start"],
                "char_end": unit["char_start"] + split_idx
            })
            processed_units.append({
                "title": unit["title"] + " (Part 2)",
                "text": unit_2_text,
                "char_start": unit["char_start"] + split_idx + 1,
                "char_end": unit["char_end"]
            })
        else:
            processed_units.append(unit)
            
    return processed_units