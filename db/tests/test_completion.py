import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from db.models import Action, CompletionCreate, EntityType
from db.orm import Completion as CompletionRow
from db.repo import (
    create_completion,
    list_active_assignments,
    list_completions_by_entity,
    list_completions_for_entities,
)

_BASE_TIME = datetime(2025, 1, 1, tzinfo=timezone.utc)


def _insert_completion(
    engine,
    entity_id: uuid.UUID,
    action: Action,
    offset_seconds: int = 0,
) -> None:
    with Session(engine) as session:
        session.add(CompletionRow(
            id=uuid.uuid4(),
            entity_type=EntityType.TASK,
            entity_id=entity_id,
            action=action,
            agent_name="agent",
            session_id="sess",
            created_at=_BASE_TIME + timedelta(seconds=offset_seconds),
        ))
        session.commit()


def test_create_completion_stores_record(engine):
    entity_id = str(uuid.uuid4())
    c = create_completion(engine, CompletionCreate(
        entity_type=EntityType.TASK,
        entity_id=entity_id,
        action=Action.STARTED,
        agent_name="agent",
        session_id="sess",
    ))
    assert c.entity_id == entity_id
    assert c.action == Action.STARTED
    assert c.agent_name == "agent"
    assert c.branch is None


def test_create_completion_stores_optional_branch(engine):
    entity_id = str(uuid.uuid4())
    c = create_completion(engine, CompletionCreate(
        entity_type=EntityType.STORY,
        entity_id=entity_id,
        action=Action.COMPLETED,
        agent_name="agent",
        session_id="sess",
        branch="main",
    ))
    assert c.branch == "main"


def test_list_completions_by_entity_returns_records(engine):
    entity_id = str(uuid.uuid4())
    create_completion(engine, CompletionCreate(
        entity_type=EntityType.TASK, entity_id=entity_id,
        action=Action.STARTED, agent_name="a", session_id="s",
    ))
    create_completion(engine, CompletionCreate(
        entity_type=EntityType.TASK, entity_id=entity_id,
        action=Action.COMPLETED, agent_name="a", session_id="s",
    ))
    results = list_completions_by_entity(engine, entity_id)
    assert len(results) == 2
    assert all(r.entity_id == entity_id for r in results)


def test_list_completions_by_entity_returns_empty_for_unknown(engine):
    assert list_completions_by_entity(engine, str(uuid.uuid4())) == []


def test_list_completions_by_entity_excludes_other_entities(engine):
    e1 = str(uuid.uuid4())
    e2 = str(uuid.uuid4())
    create_completion(engine, CompletionCreate(
        entity_type=EntityType.TASK, entity_id=e1,
        action=Action.STARTED, agent_name="a", session_id="s",
    ))
    create_completion(engine, CompletionCreate(
        entity_type=EntityType.TASK, entity_id=e2,
        action=Action.STARTED, agent_name="a", session_id="s",
    ))
    results = list_completions_by_entity(engine, e1)
    assert len(results) == 1
    assert results[0].entity_id == e1


def test_list_completions_for_entities_returns_matching(engine):
    e1 = str(uuid.uuid4())
    e2 = str(uuid.uuid4())
    e3 = str(uuid.uuid4())
    for eid in [e1, e2, e3]:
        create_completion(engine, CompletionCreate(
            entity_type=EntityType.TASK, entity_id=eid,
            action=Action.STARTED, agent_name="a", session_id="s",
        ))
    results = list_completions_for_entities(engine, [e1, e2])
    assert len(results) == 2
    assert {r.entity_id for r in results} == {e1, e2}


def test_list_completions_for_entities_empty_input(engine):
    assert list_completions_for_entities(engine, []) == []


def test_list_active_assignments_returns_entity_with_latest_started(engine):
    entity_id = uuid.uuid4()
    _insert_completion(engine, entity_id, Action.STARTED, offset_seconds=0)
    results = list_active_assignments(engine)
    assert len(results) == 1
    assert str(results[0].entity_id) == str(entity_id)


def test_list_active_assignments_excludes_when_latest_is_completed(engine):
    entity_id = uuid.uuid4()
    _insert_completion(engine, entity_id, Action.STARTED, offset_seconds=0)
    _insert_completion(engine, entity_id, Action.COMPLETED, offset_seconds=1)
    assert list_active_assignments(engine) == []


def test_list_active_assignments_includes_restarted_entity(engine):
    entity_id = uuid.uuid4()
    _insert_completion(engine, entity_id, Action.STARTED, offset_seconds=0)
    _insert_completion(engine, entity_id, Action.COMPLETED, offset_seconds=1)
    _insert_completion(engine, entity_id, Action.STARTED, offset_seconds=2)
    results = list_active_assignments(engine)
    assert len(results) == 1
    assert str(results[0].entity_id) == str(entity_id)


def test_list_active_assignments_returns_only_active_entities(engine):
    active = uuid.uuid4()
    done = uuid.uuid4()
    _insert_completion(engine, active, Action.STARTED, offset_seconds=0)
    _insert_completion(engine, done, Action.STARTED, offset_seconds=0)
    _insert_completion(engine, done, Action.COMPLETED, offset_seconds=1)
    results = list_active_assignments(engine)
    assert len(results) == 1
    assert str(results[0].entity_id) == str(active)


def test_list_active_assignments_returns_empty_when_none(engine):
    assert list_active_assignments(engine) == []
