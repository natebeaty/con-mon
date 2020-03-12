"""add cancelled flag and public_note field

Revision ID: 78427162e530
Revises: 6bb8ab2d12b3
Create Date: 2020-03-12 12:21:09.640648

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78427162e530'
down_revision = '6bb8ab2d12b3'
branch_labels = None
depends_on = None


def upgrade():
  	op.add_column('condate', sa.Column('cancelled', sa.Boolean))
  	op.add_column('condate', sa.Column('public_notes', sa.Text))


def downgrade():
  	op.drop_column('condate', 'cancelled')
  	op.drop_column('condate', 'public_notes')
