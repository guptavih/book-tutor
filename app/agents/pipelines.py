from app.agents.orchestrator import (
    extract_curriculum_from_chunk, 
    generate_exercises, 
    evaluate_user_answer,
    lesson_delivery_agent,
    error_pattern_agent
)
from app.schemas.content import ExtractedUnit, ExercisePack, FeedbackArtifact

async def run_ingestion_workflow(chapter_title: str, text: str) -> ExtractedUnit:
    """Workflow 1: Turns raw text into a structured curriculum."""
    print(f"--- Pipeline: Ingesting {chapter_title} ---")
    extracted_unit = await extract_curriculum_from_chunk(chapter_title, text)
    return extracted_unit

async def run_tutoring_workflow(module_text: str, user_question: str, mock_db: dict) -> str:
    """Workflow 2: The Tutor Loop (Lesson -> Exercise -> Feedback)."""
    print("--- Pipeline: Starting Tutoring Session ---")
    
    # 1. Lesson Delivery (Using Dependency Injection for the Tool)
    lesson_prompt = f"Here is the text to teach: {module_text}\nUser asks: {user_question}"
    lesson_result = await lesson_delivery_agent.run(lesson_prompt, deps={"mock_db": mock_db})
    
    # 2. Generate Exercises based on the lesson
    exercises = await generate_exercises(module_text, lesson_result.output.vocabulary_focus)
    
    return lesson_result.output.introduction, exercises