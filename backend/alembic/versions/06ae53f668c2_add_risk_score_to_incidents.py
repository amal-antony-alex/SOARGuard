"""add risk score to incidents"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "06ae53f668c2"
down_revision: Union[str, Sequence[str], None] = "4694fb71bdc3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "incidents",
        sa.Column(
            "risk_score",
            sa.Integer(),
            nullable=False,
            server_default="0"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "incidents",
        "risk_score"
    )
