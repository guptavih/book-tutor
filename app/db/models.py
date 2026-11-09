from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean
from datetime import datetime, UTC

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10))
    format: Mapped[str] = mapped_column(String(10))
    raw_text: Mapped[str] = mapped_column(Text)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    
    units: Mapped[list["Unit"]] = relationship(back_populates="book", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    title: Mapped[str] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    
    book: Mapped["Book"] = relationship(back_populates="units")
    modules: Mapped[list["Module"]] = relationship(back_populates="unit", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"))
    title: Mapped[str] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer)
    raw_text: Mapped[str] = mapped_column(Text)
    source_char_start: Mapped[int] = mapped_column(Integer)  
    source_char_end: Mapped[int] = mapped_column(Integer)    
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True)
    
    unit: Mapped["Unit"] = relationship(back_populates="modules")
    vocabulary: Mapped[list["VocabularyItem"]] = relationship(back_populates="module", cascade="all, delete-orphan")
    grammar: Mapped[list["GrammarPoint"]] = relationship(back_populates="module", cascade="all, delete-orphan")

class VocabularyItem(Base):
    __tablename__ = "vocabulary_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    term: Mapped[str] = mapped_column(String(255))          
    definition: Mapped[str] = mapped_column(Text)           
    example_sentence: Mapped[str] = mapped_column(Text)     
    difficulty: Mapped[int] = mapped_column(Integer, default=1)        
    
    module: Mapped["Module"] = relationship(back_populates="vocabulary")

class GrammarPoint(Base):
    __tablename__ = "grammar_points"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    rule: Mapped[str] = mapped_column(String(255))          
    explanation: Mapped[str] = mapped_column(Text)          
    is_idiom: Mapped[bool] = mapped_column(Boolean, default=False) 
    
    module: Mapped["Module"] = relationship(back_populates="grammar")
    artifacts: Mapped[list["GrammarArtifact"]] = relationship(back_populates="grammar_point")

class CurriculumGraphEdge(Base):
    __tablename__ = "curriculum_graph_edges"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source_module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    target_module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"))
    relationship_type: Mapped[str] = mapped_column(String(50))

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending") 
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class GrammarArtifact(Base):
    __tablename__ = "grammar_artifacts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    grammar_point_id: Mapped[int] = mapped_column(ForeignKey("grammar_points.id"))
    
    inductive_discovery: Mapped[str] = mapped_column(Text) 
    explicit_rule: Mapped[str] = mapped_column(Text)       
    contrastive_note: Mapped[str] = mapped_column(Text)    
    controlled_drills: Mapped[str] = mapped_column(Text)   
    free_production_prompt: Mapped[str] = mapped_column(Text) 
    
    grammar_point: Mapped["GrammarPoint"] = relationship(back_populates="artifacts")

class MistakeRecord(Base):
    __tablename__ = "mistake_records"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(Integer) # For now, just an integer ID
    module_id: Mapped[int] = mapped_column(Integer)
    exercise_id: Mapped[int] = mapped_column(Integer) # 0 for conversational mistakes
    user_answer: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    error_type: Mapped[str] = mapped_column(String(50)) # e.g., "grammar", "vocabulary"
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))