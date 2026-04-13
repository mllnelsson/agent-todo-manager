import uuid

from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import Session

from db.models import Status, Step, StepCreate, StepUpdate
from db.orm import Completion as CompletionRow
from db.orm import Step as StepRow


def _next_seq(session: Session, task_id: uuid.UUID) -> int:
    stmt = select(func.max(StepRow.seq)).where(StepRow.task_id == task_id)
    max_seq = session.execute(stmt).scalar()
    return (max_seq or 0) + 1


def _to_model(row: StepRow) -> Step:
    return Step(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        definition_of_done=row.definition_of_done,
        status=Status(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def create_step(engine: Engine, data: StepCreate) -> Step:
    tid = uuid.UUID(data.task_id)
    with Session(engine) as session:
        seq = _next_seq(session, tid)
        row = StepRow(
            id=uuid.uuid4(),
            seq=seq,
            task_id=tid,
            title=data.title,
            description=data.description,
            definition_of_done=data.definition_of_done,
            status=Status.TODO,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_model(row)


def get_step(engine: Engine, step_id: str) -> Step | None:
    with Session(engine) as session:
        row = session.get(StepRow, uuid.UUID(step_id))
        return _to_model(row) if row else None


def get_step_by_seq(engine: Engine, task_id: str, seq: int) -> Step | None:
    with Session(engine) as session:
        stmt = select(StepRow).where(
            StepRow.task_id == uuid.UUID(task_id),
            StepRow.seq == seq,
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row) if row else None


def get_next_step(engine: Engine, task_id: str) -> Step | None:
    """First TODO step in a task, ordered by seq."""
    with Session(engine) as session:
        stmt = (
            select(StepRow)
            .where(
                StepRow.task_id == uuid.UUID(task_id),
                StepRow.status == Status.TODO,
            )
            .order_by(StepRow.seq)
            .limit(1)
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row) if row else None


def update_step(engine: Engine, step_id: str, data: StepUpdate) -> Step | None:
    with Session(engine) as session:
        row = session.get(StepRow, uuid.UUID(step_id))
        if not row:
            return None
        if data.title is not None:
            row.title = data.title
        if data.description is not None:
            row.description = data.description
        if data.definition_of_done is not None:
            row.definition_of_done = data.definition_of_done
        if data.status is not None:
            row.status = data.status
        session.commit()
        session.refresh(row)
        return _to_model(row)


def delete_step(engine: Engine, step_id: str) -> bool:
    sid = uuid.UUID(step_id)
    with Session(engine) as session:
        row = session.get(StepRow, sid)
        if not row:
            return False
        session.execute(delete(CompletionRow).where(CompletionRow.entity_id == sid))
        session.delete(row)
        session.commit()
        return True
