import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

DATABASE_URL = os.environ.get("ATM_DATABASE_URL")


def create_db_engine() -> Engine:
    if not DATABASE_URL:
        raise RuntimeError(
            "ATM_DATABASE_URL is not set. "
            "Add 'export ATM_DATABASE_URL=sqlite:////absolute/path/to/app.db' "
            "to your shell config (~/.bashrc or ~/.zshrc) and restart your shell."
        )
    engine = create_engine(DATABASE_URL)

    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()

    return engine
