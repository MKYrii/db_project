import os

from sqlalchemy import create_engine

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)