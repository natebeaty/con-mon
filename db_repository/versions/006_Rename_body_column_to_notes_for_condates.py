from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    condate = Table('condate', meta, autoload=True)
    condate.c.body.alter(name='notes')

def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    condate = Table('condate', meta, autoload=True)
    condate.c.body.alter(name='body')
