from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.orchestrator import conversation_agent, conversation_feedback_agent
from app.schemas.content import ConversationTurn, ConversationFeedback
from app.db.models import MistakeRecord
import json

async def handle_conversation_turn(
    db: AsyncSession, 
    learner_id: int, 
    book_context: str, 
    learner_input: str,
    current_character: str = "The Fox"
):
    """
    Takes the learner's input, generates an in-character response, 
    and silently evaluates it for mistakes to track in the database.
    """
    
    # 1. Generate the AI in-character response
    ai_prompt = (
        f"You are roleplaying as {current_character} from the book. "
        f"Context: {book_context}. "
        f"The learner just said: '{learner_input}'. "
        f"Respond in character in the target language. Keep it short (1-2 sentences)."
    )
    ai_result = await conversation_agent.run(ai_prompt)
    
    # 2. Silently evaluate the learner's input for mistakes
    feedback_prompt = (
        f"Evaluate this sentence for grammar or spelling mistakes: '{learner_input}'. "
        f"If there are no mistakes, set has_mistake to False."
    )
    feedback_result = await conversation_feedback_agent.run(feedback_prompt) 
    feedback: ConversationFeedback = feedback_result.output
    
    # 3. If there is a mistake, track it in the database!
    if feedback.has_mistake:
        mistake = MistakeRecord(
            learner_id=learner_id,
            module_id=1, # In a real app, you'd pass the actual module ID
            exercise_id=0, # 0 denotes a conversational mistake
            user_answer=learner_input,
            correct_answer=feedback.correction or "",
            error_type=feedback.mistake_type or "unknown"
        )
        db.add(mistake)
        await db.commit()
        print(f"Logged a conversational mistake: {feedback.explanation}")

    return ai_result.output, feedback