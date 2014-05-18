from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
tag = Table('tag', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=80)),
)

tags_conventions = Table('tags_conventions', post_meta,
    Column('tag_id', Integer),
    Column('convention_id', Integer),
)

condate = Table('condate', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=80)),
    Column('body', Text),
    Column('start_date', Date),
    Column('end_date', Date),
    Column('registration_opens', Date),
    Column('registration_closes', Date),
    Column('convention_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['tag'].create()
    post_meta.tables['tags_conventions'].create()
    post_meta.tables['condate'].columns['registration_closes'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['tag'].drop()
    post_meta.tables['tags_conventions'].drop()
    post_meta.tables['condate'].columns['registration_closes'].drop()
