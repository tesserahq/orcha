"""Add parameters to nodes

Revision ID: 3c06d8ea5e18
Revises: initialize_database
Create Date: 2025-11-24 10:50:57.590701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "3c06d8ea5e18"
down_revision: Union[str, None] = "initialize_database"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "nodes",
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "edges",
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    op.alter_column(
        "nodes",
        "settings",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        new_column_name="properties",
    )

    op.alter_column(
        "edges",
        "settings",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        new_column_name="properties",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("nodes", "parameters")
    op.drop_column("edges", "parameters")
    op.alter_column(
        "nodes",
        "properties",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        new_column_name="settings",
    )

    op.alter_column(
        "edges",
        "settings",
        type_=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
        new_column_name="properties",
    )
