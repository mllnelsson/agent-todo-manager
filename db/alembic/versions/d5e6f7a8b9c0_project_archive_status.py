"""Migrate project status to binary active/archived

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
Create Date: 2026-04-29 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, Sequence[str], None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Move all projects to 'active' status; archive replaces the old completed/in_progress/todo."""
    op.execute("UPDATE projects SET status = 'active'")


def downgrade() -> None:
    """Revert all project statuses to 'todo'."""
    op.execute("UPDATE projects SET status = 'todo'")
