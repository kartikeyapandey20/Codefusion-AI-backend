"""Fixing circular import

Revision ID: c924f5e9d6c3
Revises: e6a7a5548396
Create Date: 2025-03-16 23:36:52.917365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c924f5e9d6c3'
down_revision: Union[str, None] = 'e6a7a5548396'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
