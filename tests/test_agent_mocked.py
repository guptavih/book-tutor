import pytest
from pydantic_ai.models.test import TestModel
from app.agents.orchestrator import curriculum_agent
from app.schemas.content import ExtractedUnit

@pytest.mark.asyncio
async def test_agent_extraction_with_mock():
    mock_model = TestModel()
    
    with curriculum_agent.override(model=mock_model):
        result = await curriculum_agent.run("Mock chapter text")
        
        # Changed from result.data to result.output
        assert isinstance(result.output, ExtractedUnit)
        assert isinstance(result.output.title, str)
        assert isinstance(result.output.modules, list)