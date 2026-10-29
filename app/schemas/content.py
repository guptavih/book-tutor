from pydantic import BaseModel, Field
from typing import List

class ExtractedVocabulary(BaseModel):
    term: str = Field(description="The vocabulary word in the target language")
    definition: str = Field(description="The translation or definition in English")
    example_sentence: str = Field(description="The sentence from the book using this word")
    cefr_level: str = Field(description="Estimated CEFR level: A1, A2, B1, B2, C1, or C2")
    frequency_rank: int = Field(description="Estimated frequency rank of the word (1-10000)")

class ExtractedGrammar(BaseModel):
    rule: str = Field(description="The grammar rule (e.g., Passé Composé, Plural Nouns)")
    explanation: str = Field(description="Explanation of the rule based on the text")
    example_sentence: str = Field(description="An example sentence from the text")

class ExtractedModule(BaseModel):
    title: str = Field(description="A short, descriptive title for this module")
    learning_objective: str = Field(description="What the learner will achieve (e.g., Learn common adjectives)")
    source_excerpt: str = Field(description="The exact text from the book this module covers")
    vocabulary: List[ExtractedVocabulary] = Field(description="8 to 15 vocabulary items from the excerpt")
    grammar: List[ExtractedGrammar] = Field(description="1 to 2 grammar points from the excerpt")

class ExtractedUnit(BaseModel):
    title: str = Field(description="The chapter title")
    modules: List[ExtractedModule] = Field(description="A list of modules derived from this chapter")

class LanguageLevelAnalysis(BaseModel):
    detected_language: str = Field(description="The language of the text (e.g., 'French', 'Spanish', 'English')")
    cefr_level: str = Field(description="Estimated CEFR level: A1, A2, B1, B2, C1, or C2")
    reasoning: str = Field(description="Brief explanation of why this level was chosen")