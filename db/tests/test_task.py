import uuid

from db.models import Status, TaskCreate, TaskUpdate
from db.repo import (
    create_task,
    delete_task,
    get_floating_task_by_seq,
    get_task,
    get_task_by_seq,
    list_floating_tasks,
    update_task,
)


def test_create_task_sets_todo_status(engine, project_id, story_id):
    task = create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T", description="d"))
    assert task.status == Status.TODO


def test_create_task_assigns_seq_1_for_first(engine, project_id, story_id):
    task = create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T", description="d"))
    assert task.seq == 1


def test_create_task_increments_seq_within_story(engine, project_id, story_id):
    t1 = create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T1", description="d"))
    t2 = create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T2", description="d"))
    assert t1.seq == 1
    assert t2.seq == 2


def test_create_floating_task_assigns_seq_1_for_first(engine, project_id):
    task = create_task(engine, TaskCreate(project_id=project_id, title="Bug", description="d", prefix="b"))
    assert task.seq == 1


def test_create_floating_task_increments_seq(engine, project_id):
    t1 = create_task(engine, TaskCreate(project_id=project_id, title="Bug1", description="d", prefix="b"))
    t2 = create_task(engine, TaskCreate(project_id=project_id, title="Bug2", description="d", prefix="b"))
    assert t1.seq == 1
    assert t2.seq == 2


def test_create_floating_task_seq_independent_from_story_tasks(engine, project_id, story_id):
    create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T1", description="d"))
    create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T2", description="d"))
    floating = create_task(engine, TaskCreate(project_id=project_id, title="Bug", description="d", prefix="b"))
    assert floating.seq == 1


def test_get_task_returns_task(engine, task_id):
    task = get_task(engine, task_id)
    assert task is not None
    assert task.id == task_id


def test_get_task_returns_none_when_not_found(engine):
    assert get_task(engine, str(uuid.uuid4())) is None


def test_get_task_by_seq_returns_task(engine, story_id, task_id):
    task = get_task_by_seq(engine, story_id, 1)
    assert task is not None
    assert task.id == task_id


def test_get_task_by_seq_returns_none_when_not_found(engine, story_id):
    assert get_task_by_seq(engine, story_id, 99) is None


def test_get_floating_task_by_seq_returns_task(engine, project_id):
    created = create_task(engine, TaskCreate(project_id=project_id, title="Bug", description="d", prefix="b"))
    found = get_floating_task_by_seq(engine, project_id, created.seq)
    assert found is not None
    assert found.id == created.id


def test_get_floating_task_by_seq_returns_none_when_not_found(engine, project_id):
    assert get_floating_task_by_seq(engine, project_id, 99) is None


def test_list_floating_tasks_excludes_story_tasks(engine, project_id, story_id, task_id):
    create_task(engine, TaskCreate(project_id=project_id, title="Bug", description="d", prefix="b"))
    floating = list_floating_tasks(engine, project_id)
    assert len(floating) == 1
    assert floating[0].prefix == "b"


def test_list_floating_tasks_ordered_by_seq(engine, project_id):
    create_task(engine, TaskCreate(project_id=project_id, title="Bug1", description="d", prefix="b"))
    create_task(engine, TaskCreate(project_id=project_id, title="Bug2", description="d", prefix="b"))
    floating = list_floating_tasks(engine, project_id)
    assert [t.seq for t in floating] == [1, 2]


def test_list_floating_tasks_returns_empty(engine, project_id):
    assert list_floating_tasks(engine, project_id) == []


def test_update_task_updates_title(engine, task_id):
    updated = update_task(engine, task_id, TaskUpdate(title="Updated"))
    assert updated is not None
    assert updated.title == "Updated"


def test_update_task_updates_status(engine, task_id):
    updated = update_task(engine, task_id, TaskUpdate(status=Status.IN_PROGRESS))
    assert updated is not None
    assert updated.status == Status.IN_PROGRESS


def test_update_task_ignores_none_fields(engine, task_id):
    original = get_task(engine, task_id)
    updated = update_task(engine, task_id, TaskUpdate(title=None))
    assert original is not None
    assert updated is not None
    assert updated.description == original.description


def test_update_task_returns_none_when_not_found(engine):
    assert update_task(engine, str(uuid.uuid4()), TaskUpdate(title="X")) is None


def test_delete_task_removes_it(engine, task_id):
    assert delete_task(engine, task_id) is True
    assert get_task(engine, task_id) is None


def test_delete_task_returns_false_when_not_found(engine):
    assert delete_task(engine, str(uuid.uuid4())) is False


def test_create_task_with_definition_of_done(engine, project_id, story_id):
    task = create_task(
        engine,
        TaskCreate(
            project_id=project_id,
            story_id=story_id,
            title="T",
            description="d",
            definition_of_done="All tests pass and PR approved",
        ),
    )
    assert task.definition_of_done == "All tests pass and PR approved"


def test_create_task_without_definition_of_done_defaults_to_none(engine, project_id, story_id):
    task = create_task(engine, TaskCreate(project_id=project_id, story_id=story_id, title="T", description="d"))
    assert task.definition_of_done is None


def test_update_task_sets_definition_of_done(engine, task_id):
    updated = update_task(engine, task_id, TaskUpdate(definition_of_done="Reviewed and deployed"))
    assert updated is not None
    assert updated.definition_of_done == "Reviewed and deployed"
