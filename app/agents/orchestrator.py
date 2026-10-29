from dotenv import load_dotenv
import os

load_dotenv()

from pydantic_ai import Agent
from app.schemas.content import ExtractedUnit

curriculum_agent = Agent(
    'groq:openai/gpt-oss-120b',
    output_type=ExtractedUnit,
    system_prompt=(
        "You are an expert language curriculum designer. "
        "Extract vocabulary and grammar from the provided text. "
        "IMPORTANT RULES: "
        "1. Create ONE cohesive module containing BOTH the vocabulary and grammar. Do not create separate modules for them. "
        "2. You MUST use the exact JSON keys defined in the schema. "
        "3. For vocabulary, use these keys: 'term', 'definition', 'example_sentence', 'cefr_level', 'frequency_rank'. "
        "4. For grammar, use these keys: 'rule', 'explanation', 'example_sentence'. "
        "5. Do NOT use keys like 'word', 'structure', or 'example'. "
        "6. Provide 8 to 15 vocabulary items and 1 to 2 grammar points."
    )
)

async def extract_curriculum_from_chunk(title: str, text: str) -> ExtractedUnit:
    prompt = f"Chapter Title: {title}\n\nText:\n{text}"
    result = await curriculum_agent.run(prompt)
    return result.output

from app.schemas.content import LanguageLevelAnalysis

level_detection_agent = Agent(
    'groq:openai/gpt-oss-120b',
    output_type=LanguageLevelAnalysis,
    system_prompt=(
        "You are an expert linguist. Analyze the provided text and determine its language "
        "and estimated CEFR difficulty level. Be strict but realistic."
    )
)

async def detect_language_and_level(text: str) -> LanguageLevelAnalysis:
    prompt = f"Analyze this text:\n\n{text}"
    result = await level_detection_agent.run(prompt)
    return result.output