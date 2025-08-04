"""make_fields_optional

Revision ID: 4d0ed1eb2531
Revises: 3f951f273f3d
Create Date: 2025-07-18 08:09:44.617411

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d0ed1eb2531'
down_revision: Union[str, None] = '3f951f273f3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
