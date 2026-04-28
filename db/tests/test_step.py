import uuid

from db.models import StepCreate, StepUpdate
from db.repo import (
    create_step,
    delete_step,
    get_step,
    get_step_by_seq,
    update_step,
)


def test_create_step_assigns_seq_1_for_first(engine, task_id):
    step = create_step(engine, StepCreate(task_id=task_id, title="S", description="d"))
    assert step.seq == 1


def test_create_step_increments_seq(engine, task_id):
    s1 = create_step(engine, StepCreate(task_id=task_id, title="S1", description="d"))
    s2 = create_step(engine, StepCreate(task_id=task_id, title="S2", description="d"))
    assert s1.seq == 1
    assert s2.seq == 2


def test_get_step_returns_step(engine, step_id):
    step = get_step(engine, step_id)
    assert step is not None
    assert step.id == step_id


def test_get_step_returns_none_when_not_found(engine):
    assert get_step(engine, str(uuid.uuid4())) is None


def test_get_step_by_seq_returns_step(engine, task_id, step_id):
    step = get_step_by_seq(engine, task_id, 1)
    assert step is not None
    assert step.id == step_id


def test_get_step_by_seq_returns_none_when_not_found(engine, task_id):
    assert get_step_by_seq(engine, task_id, 99) is None


def test_update_step_updates_title(engine, step_id):
    updated = update_step(engine, step_id, StepUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_step_ignores_none_fields(engine, step_id):
    original = get_step(engine, step_id)
    updated = update_step(engine, step_id, StepUpdate(title=None))
    assert original is not None
    assert updated is not None
    assert updated.description == original.description


def test_update_step_returns_none_when_not_found(engine):
    assert update_step(engine, str(uuid.uuid4()), StepUpdate(title="X")) is None


def test_delete_step_removes_it(engine, step_id):
    assert delete_step(engine, step_id) is True
    assert get_step(engine, step_id) is None


def test_delete_step_returns_false_when_not_found(engine):
    assert delete_step(engine, str(uuid.uuid4())) is False


def test_create_step_with_definition_of_done(engine, task_id):
    step = create_step(
        engine,
        StepCreate(
            task_id=task_id,
            title="S",
            description="d",
            definition_of_done="Function returns correct value for all edge cases",
        ),
    )
    assert step.definition_of_done == "Function returns correct value for all edge cases"


def test_create_step_without_definition_of_done_defaults_to_none(engine, task_id):
    step = create_step(engine, StepCreate(task_id=task_id, title="S", description="d"))
    assert step.definition_of_done is None


def test_update_step_sets_definition_of_done(engine, step_id):
    updated = update_step(engine, step_id, StepUpdate(definition_of_done="Linted and tested"))
    assert updated is not None
    assert updated.definition_of_done == "Linted and tested"
