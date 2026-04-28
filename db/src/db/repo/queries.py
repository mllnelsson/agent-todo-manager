import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from db.models import Status, Task
from db.orm import Story as StoryRow
from db.orm import Task as TaskRow

from .task import _to_model as _task_to_model


def list_stale_tasks(engine: Engine, project_id: str, days: int) -> list[Task]:
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    with Session(engine) as session:
        stmt = (
            select(TaskRow)
            .where(
                TaskRow.project_id == uuid.UUID(project_id),
                TaskRow.status != Status.COMPLETED,
                TaskRow.updated_at < cutoff,
            )
            .order_by(TaskRow.updated_at)
        )
        rows = session.execute(stmt).scalars().all()
        return [_task_to_model(r) for r in rows]


def list_orphaned_tasks(engine: Engine, project_id: str) -> list[Task]:
    with Session(engine) as session:
        completed_story_ids_stmt = select(StoryRow.id).where(
            StoryRow.project_id == uuid.UUID(project_id),
            StoryRow.status == Status.COMPLETED,
        )
        completed_story_ids = session.execute(completed_story_ids_stmt).scalars().all()
        if not completed_story_ids:
            return []
        stmt = (
            select(TaskRow)
            .where(
                TaskRow.story_id.in_(completed_story_ids),
                TaskRow.status != Status.COMPLETED,
            )
            .order_by(TaskRow.story_id, TaskRow.seq)
        )
        rows = session.execute(stmt).scalars().all()
        return [_task_to_model(r) for r in rows]


def list_todo_in_completed_stories(engine: Engine, project_id: str) -> list[Task]:
    with Session(engine) as session:
        completed_story_ids_stmt = select(StoryRow.id).where(
            StoryRow.project_id == uuid.UUID(project_id),
            StoryRow.status == Status.COMPLETED,
        )
        completed_story_ids = session.execute(completed_story_ids_stmt).scalars().all()
        if not completed_story_ids:
            return []
        stmt = (
            select(TaskRow)
            .where(
                TaskRow.story_id.in_(completed_story_ids),
                TaskRow.status == Status.TODO,
            )
            .order_by(TaskRow.story_id, TaskRow.seq)
        )
        rows = session.execute(stmt).scalars().all()
        return [_task_to_model(r) for r in rows]
