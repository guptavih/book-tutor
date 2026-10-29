import pytest
from app.db.session import AsyncSessionLocal
from app.db.models import Book, Unit, Module
from app.services.ingestion import process_book_ingestion
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_full_ingestion_pipeline():
    async with AsyncSessionLocal() as db:
        # 1. Create a mock book with Markdown chapters
        mock_text = """
# Chapter 1: The Drawing
Once upon a time, I saw a magnificent picture. It was a boa constrictor eating an elephant.

# Chapter 2: The Sheep
So I lived my life alone, until a plane crash. I asked the little prince to draw me a sheep.
"""
        book = Book(
            title="Le Petit Prince Test", author="Antoine", 
            language="fr", format="txt", raw_text=mock_text
        )
        db.add(book)
        await db.commit()
        await db.refresh(book)

        # 2. Run the pipeline
        await process_book_ingestion(db, book)

        # 3. Verify the Database
        # Check Units
        units_result = await db.execute(select(Unit).where(Unit.book_id == book.id))
        units = units_result.scalars().all()
        assert len(units) == 2
        assert units[0].is_draft == True

        # Check Modules
        modules_result = await db.execute(select(Module).where(Module.unit_id == units[0].id))
        modules = modules_result.scalars().all()
        assert len(modules) > 0
        
        print("Test passed! Successfully ingested and saved to database.")