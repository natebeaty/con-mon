from sqlalchemy import *
from migrate import *

meta = MetaData()

phrase = Table(
    'phrase', meta,
    Column('id', Integer, primary_key=True),
    Column('body', Text),
    Column('num_uses', Integer, default=0),
)


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    phrase.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    phrase.drop()