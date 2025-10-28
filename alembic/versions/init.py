"""Initialize the database

Revision ID: initialize_database
Revises:
Create Date: 2024-03-21

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "initialize_database"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FTS_EXPR = " || ".join(
    [
        "setweight(to_tsvector('simple_unaccent', coalesce(first_name,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(middle_name,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(last_name,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(company,'')), 'A')",
        "setweight(to_tsvector('simple_unaccent', coalesce(job,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(email,'')), 'B')",
        "setweight(to_tsvector('simple_unaccent', coalesce(phone,'')), 'C')",
        "setweight(to_tsvector('simple_unaccent', coalesce(notes,'')), 'C')",
        "setweight(to_tsvector('simple_unaccent', coalesce(address_line_1,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(address_line_2,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(city,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(state,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(zip_code,'')), 'D')",
        "setweight(to_tsvector('simple_unaccent', coalesce(country,'')), 'D')",
    ]
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # Create text search configuration for unaccented text search
    # Ensure simple_unaccent config exists
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_ts_config WHERE cfgname = 'simple_unaccent'
            ) THEN
                CREATE TEXT SEARCH CONFIGURATION simple_unaccent ( COPY = simple );
                ALTER TEXT SEARCH CONFIGURATION simple_unaccent ALTER MAPPING
                    FOR hword, hword_part, word WITH unaccent, simple;
            END IF;
        END$$;
        """
    )

    op.create_table(
        "app_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String, unique=True, nullable=True),
        sa.Column("username", sa.String, unique=True, nullable=True),
        sa.Column("external_id", sa.String, nullable=True),
        sa.Column("avatar_url", sa.String, nullable=True),
        sa.Column("first_name", sa.String, nullable=False),
        sa.Column("last_name", sa.String, nullable=False),
        sa.Column("provider", sa.String, nullable=True),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
        sa.Column("verified", sa.Boolean, default=False),
        sa.Column("verified_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # Add a partial unique index for external_id
    op.create_index(
        "uq_users_external_id",
        "users",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    # Create contacts table first
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint("uq_sources_identifier", "sources", ["identifier"])

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("spec_version", sa.String(), nullable=False),
        sa.Column("time", sa.DateTime(), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("trigger_event_type", sa.String(), nullable=False),
        sa.Column(
            "trigger_event_filters",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("sources")

    # Drop the partial unique index
    op.drop_index("uq_users_external_id", table_name="users")
    op.drop_table("users")
    op.drop_table("app_settings")

    # Drop text search configuration
    op.execute("DROP TEXT SEARCH CONFIGURATION IF EXISTS simple_unaccent;")
