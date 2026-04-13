"""Add definition_of_done to tasks and steps

Revision ID: b3c4d5e6f7a8
Revises: 5ba6e56e1904
Create Date: 2026-04-13 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "5ba6e56e1904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable definition_of_done column to tasks and steps."""
    op.add_column("tasks", sa.Column("definition_of_done", sa.Text(), nullable=True))
    op.add_column("steps", sa.Column("definition_of_done", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove definition_of_done column from tasks and steps."""
    op.drop_column("steps", "definition_of_done")
    op.drop_column("tasks", "definition_of_done")
