from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Book, Unit, Module, IngestionJob
from app.services.sync import delete_module_from_chroma

async def create_book(db: AsyncSession, title: str, author: str, language: str, format: str, raw_text: str):
    """Creates a book and an initial ingestion job, with validation."""
    # Validation Rule 1: Ensure format is supported
    allowed_formats = ["epub", "pdf", "docx", "txt"]
    if format.lower() not in allowed_formats:
        raise ValueError(f"Unsupported format: {format}. Must be one of {allowed_formats}")

    new_book = Book(
        title=title, author=author, language=language, 
        format=format.lower(), raw_text=raw_text
    )
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    
    # Create an ingestion job record for tracking
    job = IngestionJob(book_id=new_book.id, status="pending")
    db.add(job)
    await db.commit()
    
    return new_book

async def create_module(db: AsyncSession, unit_id: int, title: str, sequence: int, raw_text: str, char_start: int, char_end: int):
    """Creates a module and validates character offsets."""
    # Validation Rule 2: Ensure exact character offsets are valid
    if char_start >= char_end:
        raise ValueError("Validation Error: source_char_start must be less than source_char_end")
        
    new_module = Module(
        unit_id=unit_id, title=title, sequence=sequence, 
        raw_text=raw_text, source_char_start=char_start, source_char_end=char_end
    )
    db.add(new_module)
    await db.commit()
    await db.refresh(new_module)
    return new_module

async def get_book_by_id(db: AsyncSession, book_id: int):
    """Fetches a book by its ID."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()

async def delete_module(db: AsyncSession, module_id: int):
    """Deletes a module from SQLite and synchronizes the deletion to ChromaDB."""
    # 1. Delete from SQLite
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()
    
    if module:
        await db.delete(module)
        await db.commit()
        
        # 2. Inline synchronization: Delete from ChromaDB
        delete_module_from_chroma(module_id)
        return True
    return False