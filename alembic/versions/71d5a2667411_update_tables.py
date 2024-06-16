"""update tables

Revision ID: 71d5a2667411
Revises: 87331a2268af
Create Date: 2024-06-15 15:58:36.821014

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71d5a2667411'
down_revision: Union[str, None] = '87331a2268af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_items', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('order_items', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_items', 'updated_at')
    op.drop_column('order_items', 'created_at')
    # ### end Alembic commands ###