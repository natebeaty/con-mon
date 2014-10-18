from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    convention = Table('convention', meta, autoload=True)
    col = Column('twitter', String(length=250))
    col.create(convention)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    convention = Table('convention', meta, autoload=True)
    convention.c.twitter.drop()
