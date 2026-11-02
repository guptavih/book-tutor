import pytest
from pydantic_ai.models.test import TestModel
from app.agents.orchestrator import lesson_delivery_agent, session_planner_agent, error_pattern_agent
from app.agents.pipelines import run_tutoring_workflow
from app.schemas.content import ExercisePack

@pytest.mark.asyncio
async def test_lesson_delivery_with_tool_dependency_injection():
    # Use TestModel to simulate the LLM
    mock_model = TestModel()
    
    with lesson_delivery_agent.override(model=mock_model):
        # We inject a mock database via 'deps'
        mock_db = {"fox": "a small wild animal"}
        result = await lesson_delivery_agent.run(
            "Teach me about the fox.", 
            deps={"mock_db": mock_db}
        )
        
        # Verify the structured output matches our schema
        assert hasattr(result.output, "introduction")
        assert hasattr(result.output, "vocabulary_focus")

@pytest.mark.asyncio
async def test_session_planner_mock():
    with session_planner_agent.override(model=TestModel()):
        result = await session_planner_agent.run("Plan my session")
        assert hasattr(result.output, "module_id_to_study")
        assert hasattr(result.output, "estimated_time_minutes")

@pytest.mark.asyncio
async def test_error_pattern_mock():
    with error_pattern_agent.override(model=TestModel()):
        result = await error_pattern_agent.run("I keep getting the past tense wrong.")
        assert hasattr(result.output, "hypothesized_weakness")
        assert hasattr(result.output, "suggested_remedial_focus")