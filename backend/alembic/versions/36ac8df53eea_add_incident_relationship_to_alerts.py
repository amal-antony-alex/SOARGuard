"""add incident relationship to alerts

Revision ID: 36ac8df53eea
Revises: 
Create Date: 2026-09-09 18:20:25.413737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36ac8df53eea'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    with op.batch_alter_table("alerts") as batch_op:

        batch_op.add_column(
            sa.Column(
                "incident_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_foreign_key(
            "fk_alerts_incident_id",
            "incidents",
            ["incident_id"],
            ["id"]
        )

def downgrade() -> None:

    with op.batch_alter_table("alerts") as batch_op:

        batch_op.drop_constraint(
            "fk_alerts_incident_id",
            type_="foreignkey"
        )

        batch_op.drop_column(
            "incident_id"
        )