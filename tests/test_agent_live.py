import pytest
from dotenv import load_dotenv
from app.agents.orchestrator import extract_curriculum_from_chunk

load_dotenv()

@pytest.mark.asyncio
async def test_live_llm_extraction():
    title = "Chapter 1"
    text = """
    L'essentiel est invisible pour les yeux. 
    Voici mon secret. Il est très simple: on ne voit bien qu'avec le cœur.
    Les hommes ont oublié cette vérité.
    """
    
    result = await extract_curriculum_from_chunk(title, text)
    
    # result is now the ExtractedUnit object directly
    assert result.title == title
    assert len(result.modules) > 0
    
    module = result.modules[0]
    assert len(module.vocabulary) >= 8
    assert len(module.grammar) >= 1
    
    terms = [v.term.lower() for v in module.vocabulary]
    assert "essentiel" in terms or "invisible" in terms or "secret" in terms