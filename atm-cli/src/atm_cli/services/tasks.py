from db.models import Task, TaskCreate, TaskUpdate
from db.repo import (
    create_task,
    get_floating_task_by_seq,
    get_task,
    get_task_by_seq,
    list_floating_tasks,
    update_task,
)
from sqlalchemy.engine import Engine

from .exceptions import NotFound


def get_task_by_id(task_id: str, engine: Engine) -> Task:
    """Fetch a task by its UUID.

    Args:
        task_id: UUID of the task.
        engine: SQLAlchemy engine.

    Returns:
        The matching Task with its steps eagerly loaded.

    Raises:
        NotFound: If no task with the given ID exists.
    """
    task = get_task(engine, task_id=task_id)
    if task is None:
        raise NotFound(f"Task {task_id} not found")
    return task


def get_task_by_story_seq(story_id: str, seq: int, engine: Engine) -> Task:
    """Fetch a task by its story-scoped sequence number.

    Args:
        story_id: UUID of the story the task belongs to.
        seq: Story-scoped sequence number of the task.
        engine: SQLAlchemy engine.

    Returns:
        The matching Task.

    Raises:
        NotFound: If no task with the given sequence number exists in the story.
    """
    task = get_task_by_seq(engine, story_id=story_id, seq=seq)
    if task is None:
        raise NotFound(f"Task {seq} not found in story {story_id}")
    return task


def get_floating_task_by_project_seq(project_id: str, seq: int, engine: Engine) -> Task:
    """Fetch a floating (story-less) task by its project-scoped sequence number.

    Args:
        project_id: UUID of the project the floating task belongs to.
        seq: Project-scoped sequence number of the floating task.
        engine: SQLAlchemy engine.

    Returns:
        The matching floating Task.

    Raises:
        NotFound: If no floating task with the given sequence number exists in the project.
    """
    task = get_floating_task_by_seq(engine, project_id=project_id, seq=seq)
    if task is None:
        raise NotFound(f"Floating task {seq} not found in project {project_id}")
    return task


def list_floating_tasks_for_project(project_id: str, engine: Engine) -> list[Task]:
    """Return all floating (story-less) tasks for the given project.

    Args:
        project_id: UUID of the project.
        engine: SQLAlchemy engine.

    Returns:
        List of floating Task objects belonging to the project.
    """
    return list_floating_tasks(engine, project_id=project_id)


def create_task_for_story(data: TaskCreate, engine: Engine) -> Task:
    """Create a new task and return it.

    Args:
        data: Task creation payload including story_id or project_id, title, and description.
        engine: SQLAlchemy engine.

    Returns:
        The newly created Task.
    """
    return create_task(engine, data=data)


def update_task_by_id(task_id: str, data: TaskUpdate, engine: Engine) -> Task:
    """Apply partial updates to the task with the given ID.

    Args:
        task_id: UUID of the task to update.
        data: Fields to update; None values are ignored.
        engine: SQLAlchemy engine.

    Returns:
        The updated Task.

    Raises:
        NotFound: If no task with the given ID exists.
    """
    task = update_task(engine, task_id=task_id, data=data)
    if task is None:
        raise NotFound(f"Task {task_id} not found")
    return task
