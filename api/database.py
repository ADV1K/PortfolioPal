from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from sqlalchemy import event

from config import config

# SQLALCHEMY_DATABASE_URL = "sqlite:///sources.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

connect_args = {}
# connect_args = {"check_same_thread": False}  # SQLite specific

engine = create_engine(config.DATABASE_URL, connect_args=connect_args, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Turn on WAL mode for SQLite: https://stackoverflow.com/a/23661501/10230641
# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA journal_mode=WAL")
#     cursor.close()


def get_db():
    """Get a database connection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
