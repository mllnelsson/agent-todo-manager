"""Drop status column from steps

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-04-28 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove status column from steps; lifecycle is now anchored at the task level."""
    with op.batch_alter_table("steps") as batch_op:
        batch_op.drop_column("status")


def downgrade() -> None:
    """Restore status column on steps with default 'TODO'."""
    with op.batch_alter_table("steps") as batch_op:
        batch_op.add_column(
            sa.Column(
                "status",
                sa.String(length=255),
                nullable=False,
                server_default="TODO",
            )
        )
