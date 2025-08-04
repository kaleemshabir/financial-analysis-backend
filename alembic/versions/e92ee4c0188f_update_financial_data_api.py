"""update_financial_data_api

Revision ID: e92ee4c0188f
Revises: 72d2b76b727a
Create Date: 2025-07-18 07:10:22.526688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e92ee4c0188f'
down_revision: Union[str, None] = '72d2b76b727a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No schema changes were needed for this migration
    # This migration corresponds to API changes in the financial data endpoints
    # to support updating and deleting financial data, as well as better handling
    # of existing data when submitting new financial data
    pass


def downgrade() -> None:
    # No schema changes to revert
    pass
