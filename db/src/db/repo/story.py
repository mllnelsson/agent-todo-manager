import uuid

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from db.models import Status, Story, StoryCreate, StoryUpdate
from db.orm import Story as StoryRow


def _next_seq(session: Session, project_id: uuid.UUID) -> int:
    stmt = select(func.max(StoryRow.seq)).where(StoryRow.project_id == project_id)
    max_seq = session.execute(stmt).scalar()
    return (max_seq or 0) + 1


def _to_model(row: StoryRow) -> Story:
    return Story(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        status=Status(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def create_story(engine: Engine, data: StoryCreate) -> Story:
    pid = uuid.UUID(data.project_id)
    with Session(engine) as session:
        seq = _next_seq(session, pid)
        row = StoryRow(
            id=uuid.uuid4(),
            seq=seq,
            project_id=pid,
            title=data.title,
            description=data.description,
            status=Status.TODO,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_model(row)


def get_story(engine: Engine, story_id: str) -> Story | None:
    with Session(engine) as session:
        row = session.get(StoryRow, uuid.UUID(story_id))
        return _to_model(row) if row else None


def get_story_by_seq(engine: Engine, project_id: str, seq: int) -> Story | None:
    with Session(engine) as session:
        stmt = select(StoryRow).where(
            StoryRow.project_id == uuid.UUID(project_id),
            StoryRow.seq == seq,
        )
        row = session.execute(stmt).scalar_one_or_none()
        return _to_model(row) if row else None


def list_stories(engine: Engine, project_id: str) -> list[Story]:
    with Session(engine) as session:
        stmt = (
            select(StoryRow)
            .where(StoryRow.project_id == uuid.UUID(project_id))
            .order_by(StoryRow.seq)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]


def list_active_stories(engine: Engine, project_id: str) -> list[Story]:
    """Stories not yet completed, ordered by seq."""
    with Session(engine) as session:
        stmt = (
            select(StoryRow)
            .where(
                StoryRow.project_id == uuid.UUID(project_id),
                StoryRow.status != Status.COMPLETED,
            )
            .order_by(StoryRow.seq)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]


def update_story(engine: Engine, story_id: str, data: StoryUpdate) -> Story | None:
    with Session(engine) as session:
        row = session.get(StoryRow, uuid.UUID(story_id))
        if not row:
            return None
        if data.title is not None:
            row.title = data.title
        if data.description is not None:
            row.description = data.description
        if data.status is not None:
            row.status = data.status
        session.commit()
        session.refresh(row)
        return _to_model(row)


def delete_story(engine: Engine, story_id: str) -> bool:
    with Session(engine) as session:
        row = session.get(StoryRow, uuid.UUID(story_id))
        if not row:
            return False
        session.delete(row)
        session.commit()
        return True
