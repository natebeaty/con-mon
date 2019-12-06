"""add submission_hash

Revision ID: 21f6a428176a
Revises:
Create Date: 2019-12-06 14:31:17.293118

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21f6a428176a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('condate', sa.Column('submission_hash', sa.Text))


def downgrade():
    op.drop_column('condate', 'submission_hash')
