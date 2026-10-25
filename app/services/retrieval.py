import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings

# Initialize persistent Chroma client
client = chromadb.PersistentClient(path=settings.chroma_path)
collection = client.get_or_create_collection("book_excerpts")

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        # We use the Qwen3 model as specified in the architecture
        _model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")
    return _model

def embed_and_store(texts: list[str], metadatas: list[dict], ids: list[str]):
    """
    Embed texts with Qwen3 and store in ChromaDB with metadata.
    """
    model = get_embedding_model()
    # Generate 1024-dimensional normalized embeddings
    embeddings = model.encode(texts, normalize_embeddings=True).tolist()
    
    # Upsert into ChromaDB so we don't create duplicates if re-run
    collection.upsert(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )