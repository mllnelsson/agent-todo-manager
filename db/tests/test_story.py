import uuid

from sqlalchemy.orm import Session

from db.models import Status, StoryCreate, StoryUpdate
from db.orm import Project as ProjectRow
from db.repo import (
    create_story,
    delete_story,
    get_story,
    get_story_by_seq,
    list_active_stories,
    list_stories,
    update_story,
)


def test_create_story_sets_todo_status(engine, project_id):
    story = create_story(engine, StoryCreate(project_id=project_id, title="S", description="d"))
    assert story.status == Status.TODO


def test_create_story_assigns_seq_1_for_first(engine, project_id):
    story = create_story(engine, StoryCreate(project_id=project_id, title="S", description="d"))
    assert story.seq == 1


def test_create_story_increments_seq(engine, project_id):
    s1 = create_story(engine, StoryCreate(project_id=project_id, title="S1", description="d"))
    s2 = create_story(engine, StoryCreate(project_id=project_id, title="S2", description="d"))
    assert s1.seq == 1
    assert s2.seq == 2


def test_create_story_seq_scoped_per_project(engine, project_id):
    other_id = uuid.uuid4()
    with Session(engine) as session:
        session.add(ProjectRow(id=other_id, title="P2", description="d", status=Status.TODO))
        session.commit()
    create_story(engine, StoryCreate(project_id=project_id, title="S1", description="d"))
    s = create_story(engine, StoryCreate(project_id=str(other_id), title="S2", description="d"))
    assert s.seq == 1


def test_get_story_returns_story(engine, story_id):
    story = get_story(engine, story_id)
    assert story is not None
    assert story.id == story_id


def test_get_story_returns_none_when_not_found(engine):
    assert get_story(engine, str(uuid.uuid4())) is None


def test_get_story_by_seq_returns_story(engine, project_id, story_id):
    story = get_story_by_seq(engine, project_id, 1)
    assert story is not None
    assert story.id == story_id


def test_get_story_by_seq_returns_none_when_not_found(engine, project_id):
    assert get_story_by_seq(engine, project_id, 99) is None


def test_list_stories_returns_empty(engine, project_id):
    assert list_stories(engine, project_id) == []


def test_list_stories_returns_all_ordered_by_seq(engine, project_id):
    create_story(engine, StoryCreate(project_id=project_id, title="S1", description="d"))
    create_story(engine, StoryCreate(project_id=project_id, title="S2", description="d"))
    create_story(engine, StoryCreate(project_id=project_id, title="S3", description="d"))
    stories = list_stories(engine, project_id)
    assert [s.seq for s in stories] == [1, 2, 3]


def test_list_active_stories_excludes_completed(engine, project_id):
    s1 = create_story(engine, StoryCreate(project_id=project_id, title="Active", description="d"))
    s2 = create_story(engine, StoryCreate(project_id=project_id, title="Done", description="d"))
    update_story(engine, s2.id, StoryUpdate(status=Status.COMPLETED))
    active = list_active_stories(engine, project_id)
    assert len(active) == 1
    assert active[0].id == s1.id


def test_list_active_stories_includes_todo_and_in_progress(engine, project_id):
    create_story(engine, StoryCreate(project_id=project_id, title="Todo", description="d"))
    s2 = create_story(engine, StoryCreate(project_id=project_id, title="WIP", description="d"))
    update_story(engine, s2.id, StoryUpdate(status=Status.IN_PROGRESS))
    active = list_active_stories(engine, project_id)
    assert len(active) == 2


def test_update_story_updates_title(engine, story_id):
    updated = update_story(engine, story_id, StoryUpdate(title="New Title"))
    assert updated is not None
    assert updated.title == "New Title"


def test_update_story_updates_status(engine, story_id):
    updated = update_story(engine, story_id, StoryUpdate(status=Status.IN_PROGRESS))
    assert updated is not None
    assert updated.status == Status.IN_PROGRESS


def test_update_story_ignores_none_fields(engine, story_id):
    original = get_story(engine, story_id)
    updated = update_story(engine, story_id, StoryUpdate(title=None))
    assert original is not None
    assert updated is not None
    assert updated.description == original.description
    assert updated.status == original.status


def test_update_story_returns_none_when_not_found(engine):
    assert update_story(engine, str(uuid.uuid4()), StoryUpdate(title="X")) is None


def test_delete_story_removes_it(engine, story_id):
    assert delete_story(engine, story_id) is True
    assert get_story(engine, story_id) is None


def test_delete_story_returns_false_when_not_found(engine):
    assert delete_story(engine, str(uuid.uuid4())) is False
