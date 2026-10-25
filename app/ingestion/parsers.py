import re
from docling.document_converter import DocumentConverter

def parse_document(file_path: str) -> str:
    """
    Extracts structured text from EPUB, PDF, DOCX, or TXT using Docling.
    Gracefully falls back to raw text reading if parsing fails.
    """
    converter = DocumentConverter()
    try:
        result = converter.convert(file_path)
        # Export as Markdown to preserve heading hierarchies (e.g., # Chapter 1)
        markdown_text = result.document.export_to_markdown()
        return markdown_text
    except Exception as e:
        print(f"Structured parsing failed: {e}. Falling back to raw text.")
        # Graceful fallback for structureless files
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

def normalize_text(raw_text: str) -> tuple[str, list[tuple[int, int]]]:
    """
    Normalizes text (removes BOM, fixes hyphenation, collapses whitespace) 
    while preserving an offset map back to the original document.
    """
    offset_map = []
    normalized_chars = []
    
    i = 0
    while i < len(raw_text):
        char = raw_text[i]
        
        # 1. Skip BOM (Byte Order Mark) and carriage returns
        if char in ('\ufeff', '\r'):
            i += 1
            continue
            
        # 2. Handle hyphenation (e.g., "exam-\nple" -> "example")
        if char == '-' and i + 1 < len(raw_text) and raw_text[i+1] == '\n':
            i += 2 # Skip the hyphen and the newline
            continue
            
        # 3. Handle excessive whitespace
        if char.isspace():
            if normalized_chars and normalized_chars[-1] == ' ':
                i += 1
                continue
            char = ' ' # Convert newlines/tabs to standard space

        normalized_chars.append(char)
        # Map the original index (i) to the new normalized index
        offset_map.append((i, len(normalized_chars) - 1))
        i += 1

    return "".join(normalized_chars), offset_map