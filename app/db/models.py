from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Boolean
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10))
    format: Mapped[str] = mapped_column(String(10))  # e.g., "epub", "pdf"
    raw_text: Mapped[str] = mapped_column(Text)      # full extracted text
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    units: Mapped[list["Unit"]] = relationship(back_populates="book", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    title: Mapped[str] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer)
    
    book: Mapped["Book"] = relationship(back_populates="units")
    modules: Mapped[list["Module"]] = relationship(back_populates="unit", cascade="all, delete-orphan")

class Module(Base):
    __tablename__ = "modules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"))
    title: Mapped[str] = mapped_column(String(255))
    sequence: Mapped[int] = mapped_column(Integer)
    raw_text: Mapped[str] = mapped_column(Text)
    
    # Exact character offsets into the source book (Week 2 requirement)
    source_char_start: Mapped[int] = mapped_column(Integer)  
    source_char_end: Mapped[int] = mapped_column(Integer)    
    
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
    is_idiom: Mapped[bool] = mapped_column(Boolean, default=False) # Added for your regional sayings idea!
    
    module: Mapped["Module"] = relationship(back_populates="grammar")

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending") 
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)