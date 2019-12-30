"""add archived flag to conventions

Revision ID: 6bb8ab2d12b3
Revises: 21f6a428176a
Create Date: 2019-12-30 14:23:08.467022

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bb8ab2d12b3'
down_revision = '21f6a428176a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('convention', sa.Column('archived', sa.Boolean))


def downgrade():
    op.drop_column('convention', 'archived')
