"""add system account

Revision ID: ae42b423852a
Revises: 3c06d8ea5e18
Create Date: 2026-01-30 16:17:19.316600

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ae42b423852a"
down_revision: Union[str, None] = "3c06d8ea5e18"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "service_account", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "service_account")
