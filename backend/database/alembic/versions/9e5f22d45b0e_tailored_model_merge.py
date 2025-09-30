"""tailored model merge

Revision ID: 9e5f22d45b0e
Revises: 1b444a346180, 81b2800397d3
Create Date: 2025-05-18 18:34:09.089014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e5f22d45b0e'
down_revision: Union[str, None] = ('1b444a346180', '81b2800397d3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
