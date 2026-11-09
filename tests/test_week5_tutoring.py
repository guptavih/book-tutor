import pytest
from pydantic_ai.models.test import TestModel
from app.agents.orchestrator import contextual_exercise_agent, lesson_sequence_agent
from app.schemas.content import ExercisePackV2, LessonSequence

@pytest.mark.asyncio
async def test_lesson_sequence_generation():
    mock_model = TestModel()
    
    with lesson_sequence_agent.override(model=mock_model):
        result = await lesson_sequence_agent.run("Text from Le Petit Prince...")
        
        # Verify the structure matches the 6-step flow
        assert isinstance(result.output, LessonSequence)
        assert hasattr(result.output, "vocabulary_pre_teaching")
        assert hasattr(result.output, "guided_reading")
        assert hasattr(result.output, "grammar_explanation")
        assert hasattr(result.output, "closing_quiz")

@pytest.mark.asyncio
async def test_contextual_exercise_generation():
    mock_model = TestModel()
    
    with contextual_exercise_agent.override(model=mock_model):
        result = await contextual_exercise_agent.run("Text from Le Petit Prince...")
        
        assert isinstance(result.output, ExercisePackV2)
        assert len(result.output.exercises) > 0
        
        # Verify it enforces the exercise types
        first_ex = result.output.exercises[0]
        assert first_ex.exercise_type in ["cloze", "translation", "comprehension"]
        assert first_ex.source_sentence != ""