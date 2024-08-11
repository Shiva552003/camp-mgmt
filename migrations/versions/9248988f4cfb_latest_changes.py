"""latest changes

Revision ID: 9248988f4cfb
Revises: f4ab4d8113cd
Create Date: 2024-08-10 10:00:09.097465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9248988f4cfb'
down_revision = 'f4ab4d8113cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.alter_column('status',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)

    # ### end Alembic commands ###
