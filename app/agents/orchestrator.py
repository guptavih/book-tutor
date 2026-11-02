from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from app.config import settings
from app.schemas.content import (
    ExtractedUnit, LanguageLevelAnalysis, ExercisePack, FeedbackArtifact
)

load_dotenv()

def get_model_string() -> str:
    """Constructs the provider string (e.g., 'groq:model-name') dynamically."""
    return f"{settings.llm_provider}:{settings.llm_model}"

# --- New Schemas for Tutoring (Moved here for simplicity) ---
class LessonDelivery(BaseModel):
    introduction: str
    vocabulary_focus: list[str]
    grammar_focus: str
    book_excerpt_to_read: str

class SessionPlan(BaseModel):
    module_id_to_study: int
    review_vocabulary_due: list[str]
    estimated_time_minutes: int

class ErrorPatternAnalysis(BaseModel):
    observed_mistakes: list[str]
    hypothesized_weakness: str
    suggested_remedial_focus: str

# --- 1. Ingestion Agents ---
curriculum_agent = Agent(
    get_model_string(),
    output_type=ExtractedUnit,
    system_prompt=(
        "You are an expert language curriculum designer. Extract vocabulary and grammar. "
        "Use exact JSON keys: 'term', 'definition', 'example_sentence', 'cefr_level', 'frequency_rank' for vocab, "
        "and 'rule', 'explanation', 'example_sentence' for grammar. Create ONE cohesive module."
    )
)

level_detection_agent = Agent(
    get_model_string(),
    output_type=LanguageLevelAnalysis,
    system_prompt="Analyze text and determine its language and CEFR difficulty."
)

# --- 2. Tutoring Agents ---
exercise_generator_agent = Agent(
    get_model_string(),
    output_type=ExercisePack,
    system_prompt="Given a text and vocabulary, generate 3 exercises testing the learner's comprehension."
)

feedback_agent = Agent(
    get_model_string(),
    output_type=FeedbackArtifact,
    system_prompt="Grade the user's answer against the correct answer. Explain the mistake kindly."
)

session_planner_agent = Agent(
    get_model_string(),
    output_type=SessionPlan,
    system_prompt="Plan a 15-minute study session based on due review items and the next module."
)

error_pattern_agent = Agent(
    get_model_string(),
    output_type=ErrorPatternAnalysis,
    system_prompt="Analyze the user's recent mistakes to find a pattern in their learning gaps."
)

# --- 3. Lesson Delivery Agent (With Dependency Injection) ---
lesson_delivery_agent = Agent(
    get_model_string(),
    deps_type=dict, # We pass a dictionary (mock_db) as dependency
    output_type=LessonDelivery,
    system_prompt=(
        "You are a friendly language tutor. Deliver a lesson based on the provided module text. "
        "Use the 'lookup_definition' tool if the user asks what a word means."
    )
)

@lesson_delivery_agent.tool
async def lookup_definition(ctx: RunContext[dict], word: str) -> str:
    """Reusable tool to look up a word in the database."""
    mock_db = ctx.deps.get("mock_db", {})
    return mock_db.get(word.lower(), f"Definition for '{word}' not found in database.")

# --- Wrapper Functions & Fallbacks ---
async def extract_curriculum_from_chunk(title: str, text: str) -> ExtractedUnit:
    result = await curriculum_agent.run(f"Chapter Title: {title}\n\nText:\n{text}")
    return result.output

async def detect_language_and_level(text: str) -> LanguageLevelAnalysis:
    result = await level_detection_agent.run(f"Analyze this text:\n\n{text}")
    return result.output

async def generate_exercises(text: str, vocab_list: list[str]) -> ExercisePack:
    prompt = f"Text: {text}\nVocab to test: {', '.join(vocab_list)}"
    result = await exercise_generator_agent.run(prompt)
    return result.output

async def evaluate_user_answer(question: str, correct: str, user_answer: str) -> FeedbackArtifact:
    prompt = f"Question: {question}\nCorrect Answer: {correct}\nUser Answer: {user_answer}"
    result = await feedback_agent.run(prompt)
    return result.output

async def run_with_fallback(agent: Agent, prompt: str):
    """Fallback logic: Tries the primary provider, falls back to OpenAI if it fails."""
    try:
        return await agent.run(prompt)
    except Exception as e:
        print(f"Primary provider failed ({e}). Falling back to OpenAI...")
        fallback_agent = Agent('openai:gpt-4o-mini', output_type=agent.output_type)
        return await fallback_agent.run(prompt)