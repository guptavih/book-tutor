import pytest
from app.services.retrieval import embed_and_store, collection, get_embedding_model

def test_chroma_add_and_query():
    # 1. Store a mock module excerpt with all required metadata
    excerpt_text = "The fox said: 'One sees clearly only with the heart.'"
    
    metadata = {
        "book_id": 1,
        "unit_id": 1,
        "module_id": 1,
        "estimated_cefr_level": "A2",
        "vocabulary_lemmas": "fox, heart, clearly",
        "grammar_point_tags": "metaphor, dialogue"
    }
    
    embed_and_store(
        texts=[excerpt_text],
        metadatas=[metadata],
        ids=["module_1_excerpt_1"]
    )
    
    # 2. Embed the query using OUR Qwen3 model (1024 dimensions)
    model = get_embedding_model()
    query_text = "What does the fox say about seeing?"
    query_embedding = model.encode([query_text], normalize_embeddings=True).tolist()
    
    # 3. Query ChromaDB using the pre-computed embedding
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=1
    )
    
    # 4. Assert it found our text
    assert len(results["documents"][0]) == 1
    assert "fox" in results["documents"][0][0].lower()
    
    # 5. Assert the metadata is intact
    retrieved_metadata = results["metadatas"][0][0]
    assert retrieved_metadata["estimated_cefr_level"] == "A2"
    assert "fox" in retrieved_metadata["vocabulary_lemmas"]