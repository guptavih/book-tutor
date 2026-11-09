from dotenv import load_dotenv
import os
from pydantic_ai import Agent
from app.config import settings
from app.schemas.content import (
    ExtractedUnit, LanguageLevelAnalysis, ExercisePackV2, FeedbackArtifact,
    GrammarExplanationTemplate, LessonSequence, ConversationFeedback
)

load_dotenv()

def get_model_string() -> str:
    """Constructs the provider string (e.g., 'groq:model-name') dynamically."""
    return f"{settings.llm_provider}:{settings.llm_model}"

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

# --- 2. Tutoring Agents (Week 4) ---
exercise_generator_agent = Agent(
    get_model_string(),
    output_type=ExercisePackV2,
    system_prompt="Given a text and vocabulary, generate 3 exercises testing the learner's comprehension."
)

feedback_agent = Agent(
    get_model_string(),
    output_type=FeedbackArtifact,
    system_prompt="Grade the user's answer against the correct answer. Explain the mistake kindly."
)

conversation_feedback_agent = Agent(
    get_model_string(),
    output_type=ConversationFeedback,
    system_prompt=(
        "Evaluate the learner's conversational input for grammar or spelling mistakes. "
        "If there are no mistakes, set has_mistake to False."
    )
)

# --- Wrapper Functions ---
async def extract_curriculum_from_chunk(title: str, text: str) -> ExtractedUnit:
    result = await curriculum_agent.run(f"Chapter Title: {title}\n\nText:\n{text}")
    return result.output

async def detect_language_and_level(text: str) -> LanguageLevelAnalysis:
    result = await level_detection_agent.run(f"Analyze this text:\n\n{text}")
    return result.output

async def generate_exercises(text: str, vocab_list: list[str]) -> ExercisePackV2:
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


# --- Week 5 Agents ---

grammar_explainer_agent = Agent(
    get_model_string(),
    output_type=GrammarExplanationTemplate,
    system_prompt=(
        "You are an expert language teacher. Create a grammar explanation following this strict 5-step template:\n"
        "1. Inductive Discovery: Provide 3-4 examples from the text.\n"
        "2. Explicit Rule: Form, meaning, and use.\n"
        "3. Contrastive Note: Compare to English.\n"
        "4. Controlled Drills: Use book sentences.\n"
        "5. Free Production Prompt."
    )
)

contextual_exercise_agent = Agent(
    get_model_string(),
    output_type=ExercisePackV2,
    system_prompt=(
        "Generate exercises (cloze deletions, translation, or comprehension) using ONLY sentences from the provided text. "
        "Ensure they target an i+1 difficulty (60-70% success rate). "
        "Each exercise must explicitly state the source sentence."
    )
)

lesson_sequence_agent = Agent(
    get_model_string(),
    output_type=LessonSequence,
    system_prompt=(
        "You are a language tutor. Create a full lesson sequence based on the module text. "
        "Follow this exact order: vocabulary_pre_teaching, guided_reading, grammar_explanation, "
        "controlled_practice, free_production, closing_quiz."
    )
)

conversation_agent = Agent(
    get_model_string(),
    output_type=str, # Just returns chat text
    system_prompt=(
        "You are a character from the book. Role-play a scenario based on the book's plot. "
        "Speak in the target language, but adjust your vocabulary to the learner's CEFR level."
    )
)