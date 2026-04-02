from db.engine import create_db_engine
from sqlalchemy.engine import Engine

_engine: Engine | None = None


def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine, creating it on first call.

    Returns:
        Module-level Engine instance, initialised lazily on first access.
    """
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine
