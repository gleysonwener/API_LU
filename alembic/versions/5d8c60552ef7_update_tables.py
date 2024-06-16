"""update tables

Revision ID: 5d8c60552ef7
Revises: adf6ace6a7f6
Create Date: 2024-06-15 15:25:32.321488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d8c60552ef7'
down_revision: Union[str, None] = 'adf6ace6a7f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('total_order_price', sa.Numeric(precision=10, scale=2), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'total_order_price')
    # ### end Alembic commands ###
