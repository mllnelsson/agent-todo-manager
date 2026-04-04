import uuid

from sqlalchemy import Engine, delete, func, select
from sqlalchemy.orm import Session

from db.models import Action, Completion, CompletionCreate, EntityType
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


def list_completions_by_entity(engine: Engine, entity_id: str) -> list[Completion]:
    with Session(engine) as session:
        stmt = (
            select(CompletionRow)
            .where(CompletionRow.entity_id == uuid.UUID(entity_id))
            .order_by(CompletionRow.created_at)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]


def list_completions_for_entities(
    engine: Engine, entity_ids: list[str]
) -> list[Completion]:
    """All completions for a set of entity IDs, ordered by created_at."""
    if not entity_ids:
        return []
    with Session(engine) as session:
        uuids = [uuid.UUID(eid) for eid in entity_ids]
        stmt = (
            select(CompletionRow)
            .where(CompletionRow.entity_id.in_(uuids))
            .order_by(CompletionRow.created_at)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]


def delete_completions_by_entity_ids(engine: Engine, entity_ids: list[str]) -> int:
    if not entity_ids:
        return 0
    with Session(engine) as session:
        uuids = [uuid.UUID(eid) for eid in entity_ids]
        result = session.execute(
            delete(CompletionRow).where(CompletionRow.entity_id.in_(uuids))
        )
        session.commit()
        return result.rowcount


def list_active_assignments(engine: Engine) -> list[Completion]:
    """Completions where the latest record per entity_id has action=started."""
    with Session(engine) as session:
        subq = (
            select(
                CompletionRow.entity_id,
                func.max(CompletionRow.created_at).label("latest"),
            )
            .group_by(CompletionRow.entity_id)
            .subquery()
        )
        stmt = (
            select(CompletionRow)
            .join(
                subq,
                (CompletionRow.entity_id == subq.c.entity_id)
                & (CompletionRow.created_at == subq.c.latest),
            )
            .where(CompletionRow.action == Action.STARTED)
        )
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]
