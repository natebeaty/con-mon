from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    condate = Table('condate', meta, autoload=True)
    col = Column('published', Boolean, default=false)
    col.create(condate, populate_default=True)

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    condate = Table('condate', meta, autoload=True)
    condate.c.published.drop()
