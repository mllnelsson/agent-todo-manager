from db.models import Project
from db.repo import get_project
from sqlalchemy import Engine

from .exceptions import NotFound


def get_project_by_id(id: str, engine: Engine) -> Project:
    """Fetch a project by ID, including its full story/task/step tree.

    Args:
        id: UUID of the project to fetch.
        engine: SQLAlchemy engine.

    Returns:
        The matching Project with all child entities eagerly loaded.

    Raises:
        NotFound: If no project with the given ID exists.
    """
    project = get_project(engine, project_id=id)
    if project is None:
        raise NotFound(f"Project {id} not found")
    return project
