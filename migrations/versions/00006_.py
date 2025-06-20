"""empty message

Revision ID: 00006
Revises: 00005
Create Date: 2025-06-15 11:51:11.752344

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "00006"
down_revision: Union[str, None] = "00005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("countries_dial_code_key"), "countries", type_="unique")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(
        op.f("countries_dial_code_key"),
        "countries",
        ["dial_code"],
        postgresql_nulls_not_distinct=False,
    )
    # ### end Alembic commands ###
