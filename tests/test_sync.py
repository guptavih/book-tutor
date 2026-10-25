import pytest
from app.services.sync import rebuild_chroma_from_sqlite
from app.services import retrieval  # Import the module to get the updated collection
from app.db.session import AsyncSessionLocal
from app.db.crud import create_book, create_module
from app.db.models import Unit

@pytest.mark.asyncio
async def test_chroma_rebuild():
    # 1. Setup: Insert a book and module into SQLite
    async with AsyncSessionLocal() as db:
        book = await create_book(
            db, title="Test Book", author="Tester", 
            language="en", format="txt", raw_text="Full text here."
        )
        
        # Create a Unit
        unit = Unit(book_id=book.id, title="Chapter 1", sequence=1)
        db.add(unit)
        await db.commit()
        await db.refresh(unit)

        # Create a Module
        mod = await create_module(
            db, unit_id=unit.id, title="Intro", sequence=1, 
            raw_text="This is a test excerpt about a fox.", 
            char_start=0, char_end=36
        )

    # 2. Run the rebuild function
    await rebuild_chroma_from_sqlite()

    # 3. Verify the module was re-indexed in ChromaDB using the UPDATED collection
    results = retrieval.collection.get(ids=[f"module_{mod.id}"])
    assert len(results["documents"]) == 1
    assert "fox" in results["documents"][0].lower()
    assert results["metadatas"][0]["book_id"] == book.id