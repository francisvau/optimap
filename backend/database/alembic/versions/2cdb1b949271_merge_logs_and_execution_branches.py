"""merge logs and execution branches

Revision ID: 2cdb1b949271
Revises: 663c8cc84c5e, a6b59a888a1b
Create Date: 2025-05-17 22:27:35.707108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cdb1b949271'
down_revision: Union[str, None] = ('663c8cc84c5e', 'a6b59a888a1b')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
