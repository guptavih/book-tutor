from app.services import retrieval  # Import the module itself so we can update its variable
from app.db.session import AsyncSessionLocal
from app.db.models import Module
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

def delete_module_from_chroma(module_id: int):
    """Inline delete synchronization."""
    try:
        retrieval.collection.delete(ids=[f"module_{module_id}"])
        print(f"Deleted module {module_id} from ChromaDB.")
    except Exception as e:
        print(f"Failed to delete module {module_id} from ChromaDB: {e}")

async def rebuild_chroma_from_sqlite():
    """
    Full-rebuild path: deletes ChromaDB collection and reconstructs it from SQLite.
    """
    print("Starting ChromaDB full rebuild from SQLite...")
    
    # 1. Delete the existing collection
    try:
        retrieval.client.delete_collection("book_excerpts")
    except Exception:
        pass 
        
    # 2. Create a fresh collection AND update the global reference in retrieval.py
    retrieval.collection = retrieval.client.create_collection("book_excerpts")
    
    # 3. Fetch all modules from SQLite
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Module).options(selectinload(Module.unit))
        )
        modules = result.scalars().all()
        
        print(f"Found {len(modules)} modules in SQLite. Rebuilding index...")
        
        for mod in modules:
            # 4. Re-embed the text using the UPDATED collection
            retrieval.embed_and_store(
                texts=[mod.raw_text],
                metadatas=[{
                    "book_id": mod.unit.book_id,
                    "unit_id": mod.unit_id,
                    "module_id": mod.id,
                    "source_char_start": mod.source_char_start,
                    "source_char_end": mod.source_char_end
                }],
                ids=[f"module_{mod.id}"]
            )
            
    print("ChromaDB rebuild complete!")