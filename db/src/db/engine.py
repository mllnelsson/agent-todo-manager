import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

load_dotenv()

DATABASE_URL = os.environ.get("ATM_DATABASE_URL")


def create_db_engine() -> Engine:
    if not DATABASE_URL:
        raise RuntimeError("ATM_DATABASE_URL is not set")
    engine = create_engine(DATABASE_URL)

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine
