from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Book, Unit, Module, VocabularyItem, GrammarPoint, IngestionJob, CurriculumGraphEdge
from app.ingestion.chunker import structural_partition, semantic_size_enforcement
from app.agents.orchestrator import extract_curriculum_from_chunk, detect_language_and_level

async def process_book_ingestion(db: AsyncSession, book: Book):
    print(f"Starting ingestion for: {book.title}")
    
    chunks = structural_partition(book.raw_text)
    chunks = semantic_size_enforcement(chunks)
    
    job = await db.get(IngestionJob, book.id)
    if job:
        job.status = "processing"
        await db.commit()

    previous_module_id = None # Keep track of the last module to build the graph

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}: {chunk['title']}")
        
        # 1. Run Language/Level Detection on the very first chunk
        if i == 0:
            try:
                analysis = await detect_language_and_level(chunk["text"])
                print(f"Detected: {analysis.detected_language} ({analysis.cefr_level}) - {analysis.reasoning}")
                # You could save this to the Book model here if you add those columns
            except Exception as e:
                print(f"Level detection failed: {e}")

        # 2. Create the Unit
        unit = Unit(book_id=book.id, title=chunk["title"], sequence=i + 1, is_draft=True)
        db.add(unit)
        await db.commit()
        await db.refresh(unit)

        # 3. Call the LLM Agent for Curriculum
        try:
            extracted_data = await extract_curriculum_from_chunk(chunk["title"], chunk["text"])
            
            for j, ext_mod in enumerate(extracted_data.modules):
                module = Module(
                    unit_id=unit.id,
                    title=ext_mod.title,
                    sequence=j + 1,
                    raw_text=ext_mod.source_excerpt,
                    source_char_start=chunk["char_start"],
                    source_char_end=chunk["char_end"],
                    is_draft=True
                )
                db.add(module)
                await db.commit()
                await db.refresh(module)

                # 4. Build the Prerequisite Graph
                if previous_module_id is not None:
                    edge = CurriculumGraphEdge(
                        source_module_id=previous_module_id,
                        target_module_id=module.id,
                        relationship_type="prerequisite"
                    )
                    db.add(edge)
                    await db.commit()
                previous_module_id = module.id # Update for the next loop

                # Save Vocab and Grammar...
                for v in ext_mod.vocabulary:
                    db.add(VocabularyItem(
                        module_id=module.id, term=v.term, definition=v.definition,
                        example_sentence=v.example_sentence, difficulty=2
                    ))
                for g in ext_mod.grammar:
                    db.add(GrammarPoint(
                        module_id=module.id, rule=g.rule, explanation=g.explanation, is_idiom=False
                    ))
                await db.commit()
                
        except Exception as e:
            print(f"Failed to process chunk {chunk['title']}: {e}")
            await db.rollback()

    if job:
        job.status = "pending_review"
        await db.commit()
        
    print("Ingestion complete. Units, Modules, and Graph saved as drafts.")