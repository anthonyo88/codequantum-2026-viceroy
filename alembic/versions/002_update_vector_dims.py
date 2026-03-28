"""Change vector dimensions from 1536 to 768 (OpenAI → sentence-transformers)

Revision ID: 002
Revises: 001
Create Date: 2026-03-28
"""
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing vector indexes before altering column types
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")

    op.execute(
        "ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768)"
    )
    op.execute(
        "ALTER TABLE drivers ALTER COLUMN embedding_vector TYPE vector(768)"
    )

    # Recreate IVFFlat index for the new dimension
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding")

    op.execute(
        "ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536)"
    )
    op.execute(
        "ALTER TABLE drivers ALTER COLUMN embedding_vector TYPE vector(1536)"
    )

    op.execute(
        "CREATE INDEX ix_document_chunks_embedding "
        "ON document_chunks USING ivfflat (embedding vector_cosine_ops) "
        "WITH (lists = 100)"
    )
