import uuid

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session, selectinload

from db.models import Status, Step, Task, TaskCreate, TaskUpdate
from db.orm import Step as StepRow
from db.orm import Task as TaskRow


def _next_story_seq(session: Session, story_id: uuid.UUID) -> int:
    stmt = select(func.max(TaskRow.seq)).where(TaskRow.story_id == story_id)
    max_seq = session.execute(stmt).scalar()
    return (max_seq or 0) + 1


def _next_floating_seq(session: Session, project_id: uuid.UUID) -> int:
    stmt = select(func.max(TaskRow.seq)).where(
        TaskRow.project_id == project_id,
        TaskRow.story_id.is_(None),
    )
    max_seq = session.execute(stmt).scalar()
    return (max_seq or 0) + 1


def _step_to_model(row: StepRow) -> Step:
    return Step(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        status=Status(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_model(row: TaskRow, *, full: bool = False) -> Task:
    return Task(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        prefix=row.prefix,
        status=Status(row.status),
        steps=sorted([_step_to_model(s) for s in row.steps], key=lambda s: s.seq) if full else [],
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def create_task(engine: Engine, data: TaskCreate) -> Task:
    pid = uuid.UUID(data.project_id)
    sid = uuid.UUID(data.story_id) if data.story_id else None
    with Session(engine) as session:
        seq = _next_story_seq(session, sid) if sid else _next_floating_seq(session, pid)
        row = TaskRow(
            id=uuid.uuid4(),
            seq=seq,
            project_id=pid,
            story_id=sid,
            prefix=data.prefix,
            title=data.title,
            description=data.description,
            status=Status.TODO,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_model(row)


def get_task(engine: Engine, task_id: str) -> Task | None:
    with Session(engine) as session:
        stmt = (
            select(TaskRow)
            .where(TaskRow.id == uuid.UUID(task_id))
            .options(selectinload(TaskRow.steps))
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row, full=True) if row else None


def get_task_by_seq(engine: Engine, story_id: str, seq: int) -> Task | None:
    """Look up a story task by its seq within that story."""
    with Session(engine) as session:
        stmt = (
            select(TaskRow)
            .where(TaskRow.story_id == uuid.UUID(story_id), TaskRow.seq == seq)
            .options(selectinload(TaskRow.steps))
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row, full=True) if row else None


def get_floating_task_by_seq(engine: Engine, project_id: str, seq: int) -> Task | None:
    """Look up a floating task (bug/hotfix) by its project-scoped seq."""
    with Session(engine) as session:
        stmt = (
            select(TaskRow)
            .where(
                TaskRow.project_id == uuid.UUID(project_id),
                TaskRow.story_id.is_(None),
                TaskRow.seq == seq,
            )
            .options(selectinload(TaskRow.steps))
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row, full=True) if row else None


def list_floating_tasks(engine: Engine, project_id: str) -> list[Task]:
    """All tasks with no parent story (bugs, hotfixes, etc.)."""
    with Session(engine) as session:
        stmt = (
            select(TaskRow)
            .where(
                TaskRow.project_id == uuid.UUID(project_id),
                TaskRow.story_id.is_(None),
            )
            .order_by(TaskRow.seq)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]


def update_task(engine: Engine, task_id: str, data: TaskUpdate) -> Task | None:
    with Session(engine) as session:
        row = session.get(TaskRow, uuid.UUID(task_id))
        if not row:
            return None
        if data.title is not None:
            row.title = data.title
        if data.description is not None:
            row.description = data.description
        if data.status is not None:
            row.status = data.status
        if data.prefix is not None:
            row.prefix = data.prefix
        session.commit()
        session.refresh(row)
        return _to_model(row)


def delete_task(engine: Engine, task_id: str) -> bool:
    with Session(engine) as session:
        row = session.get(TaskRow, uuid.UUID(task_id))
        if not row:
            return False
        session.delete(row)
        session.commit()
        return True
