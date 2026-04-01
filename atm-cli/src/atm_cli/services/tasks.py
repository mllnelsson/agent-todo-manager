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
    task = get_task(engine, task_id=task_id)
    if task is None:
        raise NotFound(f"Task {task_id} not found")
    return task


def get_task_by_story_seq(story_id: str, seq: int, engine: Engine) -> Task:
    task = get_task_by_seq(engine, story_id=story_id, seq=seq)
    if task is None:
        raise NotFound(f"Task {seq} not found in story {story_id}")
    return task


def get_floating_task_by_project_seq(project_id: str, seq: int, engine: Engine) -> Task:
    task = get_floating_task_by_seq(engine, project_id=project_id, seq=seq)
    if task is None:
        raise NotFound(f"Floating task {seq} not found in project {project_id}")
    return task


def list_floating_tasks_for_project(project_id: str, engine: Engine) -> list[Task]:
    return list_floating_tasks(engine, project_id=project_id)


def create_task_for_story(data: TaskCreate, engine: Engine) -> Task:
    return create_task(engine, data=data)


def update_task_by_id(task_id: str, data: TaskUpdate, engine: Engine) -> Task:
    task = update_task(engine, task_id=task_id, data=data)
    if task is None:
        raise NotFound(f"Task {task_id} not found")
    return task
