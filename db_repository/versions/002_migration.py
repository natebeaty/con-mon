from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
tag = Table('tag', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=80)),
)

tags_conventions = Table('tags_conventions', pre_meta,
    Column('tag_id', INTEGER),
    Column('convention_id', INTEGER),
)

condate = Table('condate', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('title', VARCHAR(length=80)),
    Column('body', TEXT),
    Column('start_date', DATE),
    Column('end_date', DATE),
    Column('registration_opens', DATE),
    Column('convention_id', INTEGER),
    Column('registration_closes', DATE),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['tag'].drop()
    pre_meta.tables['tags_conventions'].drop()
    pre_meta.tables['condate'].columns['registration_closes'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['tag'].create()
    pre_meta.tables['tags_conventions'].create()
    pre_meta.tables['condate'].columns['registration_closes'].create()
