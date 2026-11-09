import pytest
from pydantic_ai.models.test import TestModel
from sqlalchemy.future import select
from app.services.conversation import handle_conversation_turn
from app.db.session import AsyncSessionLocal
from app.db.models import MistakeRecord

@pytest.mark.asyncio
async def test_conversation_and_error_tracking():
    async with AsyncSessionLocal() as db:
        # We use TestModel to mock both agents inside the service
        # (Note: In a real test, you'd use function models to return specific data)
        # Here we just ensure the pipeline runs without crashing and saves the record.
        
        # TestModel automatically fills data. For FeedbackArtifact, it will set has_mistake=True
        # because booleans default to True in Pydantic if not specified by the mock logic.
        
        ai_response, feedback = await handle_conversation_turn(
            db=db,
            learner_id=99,
            book_context="The fox and the prince meet in the desert.",
            learner_input="Je suis tres heureux de te voir.", # Missing accent on très
            current_character="The Fox"
        )
        
        # Verify the AI responded
        assert ai_response is not None
        
        # Verify the mistake was tracked in the DB
        result = await db.execute(select(MistakeRecord).where(MistakeRecord.learner_id == 99))
        mistakes = result.scalars().all()
        
        assert len(mistakes) > 0
        assert mistakes[-1].user_answer == "Je suis tres heureux de te voir."
        
        print("Conversation test passed! Mistake was logged to the database.")