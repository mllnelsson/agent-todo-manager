import uuid

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from db.model import Action, Completion, CompletionCreate, EntityType
from db.orm import Completion as CompletionRow


def _to_model(row: CompletionRow) -> Completion:
    return Completion(
        id=str(row.id),
        entity_type=EntityType(row.entity_type),
        entity_id=str(row.entity_id),
        action=Action(row.action),
        agent_name=row.agent_name,
        session_id=row.session_id,
        branch=row.branch,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def create_completion(engine: Engine, data: CompletionCreate) -> Completion:
    with Session(engine) as session:
        row = CompletionRow(
            id=uuid.uuid4(),
            entity_type=data.entity_type,
            entity_id=uuid.UUID(data.entity_id),
            action=data.action,
            agent_name=data.agent_name,
            session_id=data.session_id,
            branch=data.branch,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_model(row)


def get_completion(engine: Engine, completion_id: str) -> Completion | None:
    with Session(engine) as session:
        row = session.get(CompletionRow, uuid.UUID(completion_id))
        return _to_model(row) if row else None


def list_completions_by_entity(engine: Engine, entity_id: str) -> list[Completion]:
    with Session(engine) as session:
        stmt = (
            select(CompletionRow)
            .where(CompletionRow.entity_id == uuid.UUID(entity_id))
            .order_by(CompletionRow.created_at)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]
