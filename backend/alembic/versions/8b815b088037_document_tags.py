"""document_tags

Revision ID: 8b815b088037
Revises: 6f8a2c3d9e4b
Create Date: 2026-06-11 12:27:08.367128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b815b088037'
down_revision: Union[str, Sequence[str], None] = '6f8a2c3d9e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('documents', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('keywords', sa.JSON(), nullable=True))
    op.add_column('documents', sa.Column('suggested_category_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'suggested_category_id')
    op.drop_column('documents', 'keywords')
    op.drop_column('documents', 'summary')
