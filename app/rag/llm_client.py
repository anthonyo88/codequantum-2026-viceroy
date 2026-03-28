import json

from openai import AsyncOpenAI

from app.config import settings


class LLMClient:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def get_embedding(self, text: str) -> list[float]:
        response = await self._client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    async def rank_drivers(self, query: str, prompt: str, max_results: int) -> dict:
        """
        Ask GPT-4o to rank drivers from the retrieved context.
        Returns {"ranked_drivers": [{"driver_id": str, "reason": str}, ...],
                 "explanation": str, "token_count": int}
        """
        response = await self._client.chat.completions.create(
            model=settings.openai_chat_model,
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

        # Build a combined explanation from individual reasons
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
