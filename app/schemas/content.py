from pydantic import BaseModel, Field
from typing import List, Literal

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

class GrammarExplanationTemplate(BaseModel):
    inductive_discovery: str = Field(description="3-4 highlighted examples from the text to discover the rule")
    explicit_rule: str = Field(description="Explicit rule with form/meaning/use breakdown")
    contrastive_note: str = Field(description="Contrastive note against the learner's native language (English)")
    controlled_drills: str = Field(description="Drills using actual sentences from the book")
    free_production_prompt: str = Field(description="One free-production prompt requiring the structure")

class ContextualExercise(BaseModel):
    # Change str to Literal with the exact allowed values
    exercise_type: Literal["cloze", "translation", "comprehension"] = Field(
        description="Must be exactly one of these three types"
    )
    source_sentence: str = Field(description="The exact sentence from the book this is based on")
    question: str
    correct_answer: str
    rationale: str = Field(description="Why this targets a 60-70% success rate (i+1 principle)")

class ExercisePackV2(BaseModel):
    exercises: list[ContextualExercise]

class LessonSequence(BaseModel):
    vocabulary_pre_teaching: str = Field(description="Introduction to 8-15 words")
    guided_reading: str = Field(description="Excerpt with glosses and comprehension checks")
    grammar_explanation: GrammarExplanationTemplate | str = Field(description="The 5-step template OR a brief rule-only reminder if recurring")
    controlled_practice: str
    free_production: str
    closing_quiz: str

class ConversationTurn(BaseModel):
    character_name: str = Field(description="The character the AI is role-playing (e.g., 'The Fox')")
    ai_response: str = Field(description="What the character says back to the learner in the target language")
    english_translation: str = Field(description="English translation to help the learner")

class ConversationFeedback(BaseModel):
    has_mistake: bool
    mistake_type: str | None = Field(description="e.g., 'grammar', 'vocabulary', 'spelling'")
    correction: str | None = Field(description="The corrected version of the learner's sentence")
    explanation: str | None = Field(description="Brief explanation of the mistake")