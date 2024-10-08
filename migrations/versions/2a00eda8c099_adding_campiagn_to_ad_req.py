"""adding campiagn to ad_req

Revision ID: 2a00eda8c099
Revises: f0dd32f3c38e
Create Date: 2024-08-12 01:06:09.648533

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a00eda8c099'
down_revision = 'f0dd32f3c38e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.add_column(sa.Column('campaign_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'campaign', ['campaign_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ad_request', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('campaign_id')

    # ### end Alembic commands ###
