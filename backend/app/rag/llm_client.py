import asyncio
import json
from typing import Optional

from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer

from app.config import settings

# Module-level cache — loaded once, reused across all tasks and requests
_st_model: Optional[SentenceTransformer] = None


def _get_st_model() -> SentenceTransformer:
    global _st_model
    if _st_model is None:
        _st_model = SentenceTransformer(settings.embedding_model)
    return _st_model


class LLMClient:
    def __init__(self) -> None:
        # Groq uses the OpenAI-compatible API — just a different base_url
        self._client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    async def get_embedding(self, text: str) -> list[float]:
        """Generate a 768-dim embedding using sentence-transformers (local, free)."""
        loop = asyncio.get_event_loop()
        model = _get_st_model()
        # sentence-transformers is synchronous — run in thread pool to avoid blocking
        embedding = await loop.run_in_executor(None, model.encode, text)
        return embedding.tolist()

    async def rank_drivers(self, query: str, prompt: str, max_results: int) -> dict:
        """
        Ask Groq (Llama) to rank drivers from the retrieved context.
        Returns {"ranked_drivers": [{"driver_id": str, "reason": str}, ...],
                 "explanation": str, "token_count": int}
        """
        response = await self._client.chat.completions.create(
            model=settings.groq_chat_model,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert F1 driver recruiting assistant. "
                        "Return only valid JSON matching the requested schema."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        token_count = response.usage.total_tokens if response.usage else 0
        raw = response.choices[0].message.content or "{}"

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}

        ranked = data.get("ranked_drivers", [])[:max_results]

        if ranked:
            lines = [f"{i+1}. {r.get('reason', '')}" for i, r in enumerate(ranked)]
            explanation = f"Top matches for '{query}':\n" + "\n".join(lines)
        else:
            explanation = "No matching drivers found for the given criteria."

        return {
            "ranked_drivers": ranked,
            "explanation": explanation,
            "token_count": token_count,
        }
