"""add created at to alerts"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "79a459354e9d"
down_revision: Union[str, Sequence[str], None] = "560e09c38024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=True
            )
        )

    # Backfill existing alerts
    op.execute(
        """
        UPDATE alerts
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    # Make the column mandatory for all future alerts
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False
        )


def downgrade() -> None:
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.drop_column("created_at")