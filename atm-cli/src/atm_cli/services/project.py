from db.models import Project
from db.repo import get_project
from sqlalchemy import Engine

from .utils import NotFound


def get_project_by_id(id: str, engine: Engine) -> Project:
    """TODO: improve this string. This one returns the complete project tree"""
    project = get_project(engine, project_id=id)
    if project is None:
        raise NotFound(f"Project {id} not found")
    return project
