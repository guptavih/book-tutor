import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text  # <-- We need to import text

@pytest.mark.asyncio
async def test_database_connection():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.connect() as conn:
        # Use text() around the raw SQL string
        result = await conn.execute(text("SELECT 1")) 
        assert result.scalar() == 1
    await engine.dispose()