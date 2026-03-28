"""Initial schema with pgvector

Revision ID: 001
Revises:
Create Date: 2026-03-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # --- teams ---
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ergast_constructor_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("first_season", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ergast_constructor_id"),
    )

    # --- drivers ---
    op.create_table(
        "drivers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ergast_driver_id", sa.String(100), nullable=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("biography", sa.Text(), nullable=True),
        sa.Column("profile_image_url", sa.String(500), nullable=True),
        sa.Column("license_grade", sa.String(50), nullable=True),
        sa.Column("active_status", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("embedding_vector", pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ergast_driver_id"),
    )

    # --- driver_career_stats ---
    op.create_table(
        "driver_career_stats",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("total_race_starts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_podiums", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_pole_positions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_fastest_laps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_championship_points", sa.Float(), nullable=False, server_default="0"),
        sa.Column("championships_won", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("career_win_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("career_podium_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("dnf_rate", sa.Float(), nullable=False, server_default="0"),
        sa.Column("avg_qualifying_position", sa.Float(), nullable=True),
        sa.Column("avg_finish_position", sa.Float(), nullable=True),
        sa.Column("seasons_active", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("teams_driven_for", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("active_status", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_race_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("driver_id"),
    )

    # --- circuits ---
    op.create_table(
        "circuits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ergast_circuit_id", sa.String(100), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ergast_circuit_id"),
    )

    # --- driver_seasons ---
    op.create_table(
        "driver_seasons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("championship_position", sa.Integer(), nullable=True),
        sa.Column("points", sa.Float(), nullable=False, server_default="0"),
        sa.Column("wins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("podiums", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("poles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fastest_laps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("races_entered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dnfs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("teammate_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("teammate_qualifying_delta", sa.Float(), nullable=True),
        sa.Column("teammate_race_delta", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- race_results ---
    op.create_table(
        "race_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("circuit_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("season_year", sa.Integer(), nullable=False),
        sa.Column("race_name", sa.String(200), nullable=False),
        sa.Column("race_date", sa.Date(), nullable=True),
        sa.Column("grid_position", sa.Integer(), nullable=True),
        sa.Column("finish_position", sa.Integer(), nullable=True),
        sa.Column("points", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("fastest_lap", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("lap_count", sa.Integer(), nullable=True),
        sa.Column("team_name", sa.String(200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["circuit_id"], ["circuits.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- companies ---
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("company_type", sa.String(50), nullable=False, server_default="other"),
        sa.Column("subscription_tier", sa.String(50), nullable=False, server_default="free"),
        sa.Column("contact_email", sa.String(254), nullable=False),
        sa.Column("api_key_hash", sa.String(256), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("query_quota_monthly", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("queries_used_this_month", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contact_email"),
    )

    # --- company_users ---
    op.create_table(
        "company_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="scout"),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # --- shortlists ---
    op.create_table(
        "shortlists",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("driver_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("notes", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- search_queries ---
    op.create_table(
        "search_queries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("query_type", sa.String(50), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("filters_applied", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("driver_ids_returned", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("llm_response", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- document_chunks ---
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("embedding_model", sa.String(100), nullable=False, server_default="text-embedding-3-large"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["driver_id"], ["drivers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes
    op.create_index("ix_drivers_nationality", "drivers", ["nationality"])
    op.create_index("ix_drivers_active_status", "drivers", ["active_status"])
    op.create_index("ix_driver_seasons_season_year", "driver_seasons", ["season_year"])
    op.create_index("ix_race_results_season_year", "race_results", ["season_year"])
    op.create_index("ix_race_results_driver_id", "race_results", ["driver_id"])
    op.create_index("ix_document_chunks_driver_id", "document_chunks", ["driver_id"])
    op.create_index("ix_document_chunks_source_type", "document_chunks", ["source_type"])

    # Vector index for similarity search (IVFFlat — good enough for Phase 1)
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding ON document_chunks "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_table("document_chunks")
    op.drop_table("search_queries")
    op.drop_table("shortlists")
    op.drop_table("company_users")
    op.drop_table("companies")
    op.drop_table("race_results")
    op.drop_table("driver_seasons")
    op.drop_table("circuits")
    op.drop_table("driver_career_stats")
    op.drop_table("drivers")
    op.drop_table("teams")
    op.execute("DROP EXTENSION IF EXISTS vector")
