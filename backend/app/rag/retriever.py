from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


class RAGRetriever:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(self, query_embedding: list[float], top_k: int) -> list[DocumentChunk]:
        """
        Return the top-k DocumentChunks ordered by cosine similarity to query_embedding.
        Uses pgvector's <=> (cosine distance) operator.
        """
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        return list(result.scalars().all())
