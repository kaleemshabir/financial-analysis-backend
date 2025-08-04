"""make_fields_optional

Revision ID: 3f951f273f3d
Revises: e92ee4c0188f
Create Date: 2025-07-18 08:08:00.167684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision: str = '3f951f273f3d'
down_revision: Union[str, None] = 'e92ee4c0188f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN directly, so we need to use batch operations
    with op.batch_alter_table('financial_data') as batch_op:
        # Make total_liabilities nullable
        batch_op.alter_column('total_liabilities',
                existing_type=sa.Float(),
                nullable=True)
        
        # Make earning_power nullable
        batch_op.alter_column('earning_power',
                existing_type=sa.Float(),
                nullable=True)


def downgrade() -> None:
    # Revert changes if needed
    with op.batch_alter_table('financial_data') as batch_op:
        # Make total_liabilities non-nullable again
        batch_op.alter_column('total_liabilities',
                existing_type=sa.Float(),
                nullable=False)
        
        # Make earning_power non-nullable again
        batch_op.alter_column('earning_power',
                existing_type=sa.Float(),
                nullable=False)
