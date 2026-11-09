from app.db.models import GrammarPoint, GrammarArtifact
from app.agents.orchestrator import grammar_explainer_agent, lesson_sequence_agent
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

async def generate_grammar_explanation(db: AsyncSession, grammar_point_id: int, text_context: str, is_recurring: bool):
    """
    Adapts explanation depth based on whether the learner has seen this before.
    """
    if is_recurring:
        # If recurring, just give a quick rule-only reminder
        return "Rule-only reminder: Remember to use the correct auxiliary verb with the past participle."
    
    # First encounter: Generate the full 5-step template
    result = await grammar_explainer_agent.run(f"Teach this grammar using the text: {text_context}")
    template = result.output
    
    # Save as a reusable artifact
    artifact = GrammarArtifact(
        grammar_point_id=grammar_point_id,
        inductive_discovery=template.inductive_discovery,
        explicit_rule=template.explicit_rule,
        contrastive_note=template.contrastive_note,
        controlled_drills=template.controlled_drills,
        free_production_prompt=template.free_production_prompt
    )
    db.add(artifact)
    await db.commit()
    
    return template