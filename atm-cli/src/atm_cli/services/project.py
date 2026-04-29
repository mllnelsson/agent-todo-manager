from db.models import Project, ProjectStatus
from db.repo import (
    get_project,
    get_project_id_for_story,
    get_project_id_for_task,
    get_project_status,
    get_task_id_for_step,
)
from sqlalchemy import Engine

from .exceptions import NotFound, ProjectArchived


def assert_project_active_by_id(project_id: str, engine: Engine) -> None:
    """Raise ProjectArchived if the project is archived, NotFound if it doesn't exist."""
    status = get_project_status(engine, project_id)
    if status is None:
        raise NotFound(f"Project {project_id} not found")
    if status == ProjectStatus.ARCHIVED:
        raise ProjectArchived(f"Project {project_id} is archived and cannot be modified")


def assert_project_active_for_task(task_id: str, engine: Engine) -> None:
    """Raise ProjectArchived if the task's project is archived."""
    project_id = get_project_id_for_task(engine, task_id)
    if project_id is None:
        raise NotFound(f"Task {task_id} not found")
    assert_project_active_by_id(project_id, engine)


def assert_project_active_for_story(story_id: str, engine: Engine) -> None:
    """Raise ProjectArchived if the story's project is archived."""
    project_id = get_project_id_for_story(engine, story_id)
    if project_id is None:
        raise NotFound(f"Story {story_id} not found")
    assert_project_active_by_id(project_id, engine)


def assert_project_active_for_step(step_id: str, engine: Engine) -> None:
    """Raise ProjectArchived if the step's parent task's project is archived."""
    task_id = get_task_id_for_step(engine, step_id)
    if task_id is None:
        raise NotFound(f"Step {step_id} not found")
    assert_project_active_for_task(task_id, engine)


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
