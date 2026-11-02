import pytest
from app.agents.orchestrator import generate_exercises, evaluate_user_answer
from app.schemas.content import ExercisePack, FeedbackArtifact

@pytest.mark.asyncio
async def test_exercise_generation_and_feedback():
    text = "The fox said: 'One sees clearly only with the heart.'"
    vocab = ["fox", "clearly", "heart"]

    # 1. Test Exercise Generator
    exercises = await generate_exercises(text, vocab)
    assert isinstance(exercises, ExercisePack)
    assert len(exercises.exercises) > 0
    
    first_ex = exercises.exercises[0]
    assert first_ex.question != ""
    
    # 2. Test Feedback Agent
    feedback = await evaluate_user_answer(
        question=first_ex.question,
        correct=first_ex.correct_answer,
        user_answer="This is a wrong answer" # Intentionally wrong
    )
    
    assert isinstance(feedback, FeedbackArtifact)
    assert feedback.is_correct is False
    assert feedback.explanation != ""