"""added status to ad_request

Revision ID: f4ab4d8113cd
Revises: f71fb5992855
Create Date: 2024-08-09 14:15:43.869879

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4ab4d8113cd'
down_revision = 'f71fb5992855'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=10), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.drop_column('status')

    # ### end Alembic commands ###
