from pydantic import BaseModel, Field
from typing import List

# --- Shared Base Contract ---
class LinkedContext(BaseModel):
    """Every agent output must carry this to preserve state."""
    book_id: int
    unit_id: int
    module_id: int

# --- Ingestion Schemas ---
class ExtractedVocabulary(LinkedContext):
    term: str
    definition: str
    example_sentence: str
    cefr_level: str
    frequency_rank: int

class ExtractedGrammar(LinkedContext):
    rule: str
    explanation: str
    example_sentence: str

class ExtractedModule(BaseModel):
    title: str
    learning_objective: str
    source_excerpt: str
    vocabulary: List[ExtractedVocabulary]
    grammar: List[ExtractedGrammar]

class ExtractedUnit(BaseModel):
    title: str
    modules: List[ExtractedModule]

class LanguageLevelAnalysis(BaseModel):
    detected_language: str
    cefr_level: str
    reasoning: str

# --- Tutoring Schemas (Week 4 Additions) ---
class Exercise(BaseModel):
    question: str
    correct_answer: str
    exercise_type: str # e.g., "fill-in-the-blank", "multiple choice"

class ExercisePack(BaseModel):
    module_id: int
    exercises: List[Exercise]

class FeedbackArtifact(BaseModel):
    exercise_question: str
    user_answer: str
    is_correct: bool
    explanation: str
    suggested_review: str | None = None