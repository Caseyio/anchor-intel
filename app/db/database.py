from databases import Database
import sqlalchemy
from sqlalchemy import create_engine
from . import tables  # noqa: F401  # ensures metadata is populated before create_all()

# Database setup
DATABASE_URL = "postgresql+psycopg2://caseyortiz@localhost/liquor_store"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
engine = create_engine(DATABASE_URL)
