import os

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    create_engine
)
from databases import Database


DATABASE_URL = os.getenv('DATABASE_URL')


engine = create_engine(DATABASE_URL)
metadata = MetaData()
inbox = Table(
    'inbox',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('request_code', Integer),
    Column('file_name', String, unique=True),
    Column('date_created', DateTime, nullable=False),
)


database = Database(DATABASE_URL)
