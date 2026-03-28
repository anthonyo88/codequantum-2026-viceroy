from app.config import settings
from app.models.document_chunk import DocumentChunk

# Rough token estimate: 4 chars ≈ 1 token
_CHARS_PER_TOKEN = 4


def build_ranking_prompt(
    query: str, chunks: list[DocumentChunk], max_results: int
) -> str:
    """
    Build a prompt for GPT-4o to rank drivers from retrieved chunks.
    Respects settings.rag_context_token_budget by truncating chunks if needed.
    """
    token_budget = settings.rag_context_token_budget
    header = (
        f"You are an F1 driver recruiting assistant. "
        f"A recruiter is looking for drivers matching the following criteria:\n\n"
        f"QUERY: {query}\n\n"
        f"Below are summaries of F1 drivers from the database. "
        f"Based on the query, rank the most relevant drivers and explain why each matches.\n\n"
    )
    footer = (
        f'\nReturn a JSON object with this exact schema:\n'
        f'{{"ranked_drivers": [{{"driver_id": "<uuid>", "reason": "<1-2 sentence explanation>"}}]}}\n'
        f"Return at most {max_results} drivers. "
        f"Only include drivers that genuinely match the criteria. "
        f"Use the driver_id values exactly as provided in the context."
    )

    budget_chars = token_budget * _CHARS_PER_TOKEN
    used_chars = len(header) + len(footer)

    # Group chunks by driver to deduplicate and build richer per-driver context
    # (bio + career_stats together give the LLM more signal per driver)
    seen_driver_ids: set = set()
    context_parts: list[str] = []

    for chunk in chunks:
        driver_id = str(chunk.driver_id)
        chunk_text = f"[driver_id: {driver_id}]\n{chunk.content}"
        chunk_chars = len(chunk_text) + 4  # 4 for separator "---\n"

        if used_chars + chunk_chars > budget_chars:
            break

        context_parts.append(chunk_text)
        seen_driver_ids.add(driver_id)
        used_chars += chunk_chars

    context = "\n---\n".join(context_parts)
    return header + context + footer
