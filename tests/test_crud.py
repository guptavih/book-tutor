import pytest
from app.db.session import AsyncSessionLocal
from app.db.crud import create_book, get_book_by_id
from app.db.models import Base
from app.db.session import engine

@pytest.mark.asyncio
async def test_create_and_validate_book():
    # Create a fresh DB for testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # 1. Test valid book creation
        book = await create_book(
            db, title="Le Petit Prince", author="Antoine de Saint-Exupéry", 
            language="fr", format="epub", raw_text="Once upon a time..."
        )
        assert book.id is not None
        assert book.title == "Le Petit Prince"
        
        # 2. Test fetching the book
        fetched_book = await get_book_by_id(db, book.id)
        assert fetched_book.title == "Le Petit Prince"

        # 3. Test Validation Rule: Invalid Format
        with pytest.raises(ValueError, match="Unsupported format"):
            await create_book(
                db, title="Bad Book", author="Unknown", 
                language="en", format="jpg", raw_text="..."
            )