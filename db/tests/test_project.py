import uuid

from sqlalchemy.orm import Session

from db.models import Status
from db.orm import Project as ProjectRow
from db.orm import Story as StoryRow
from db.orm import Task as TaskRow
from db.repo import get_project, list_active_projects, list_projects


def _insert_project(engine, status: Status = Status.TODO) -> str:
    pid = uuid.uuid4()
    with Session(engine) as session:
        session.add(ProjectRow(
            id=pid,
            title="Project",
            description="d",
            status=status,
        ))
        session.commit()
    return str(pid)


def test_list_projects_returns_empty(engine):
    assert list_projects(engine) == []


def test_list_projects_returns_all(engine):
    _insert_project(engine)
    _insert_project(engine)
    assert len(list_projects(engine)) == 2


def test_list_active_projects_excludes_completed(engine):
    _insert_project(engine, Status.TODO)
    _insert_project(engine, Status.IN_PROGRESS)
    _insert_project(engine, Status.COMPLETED)
    result = list_active_projects(engine)
    assert len(result) == 2
    assert all(p.status != Status.COMPLETED for p in result)


def test_list_active_projects_returns_empty_when_all_completed(engine):
    _insert_project(engine, Status.COMPLETED)
    assert list_active_projects(engine) == []


def test_get_project_returns_none_when_not_found(engine):
    assert get_project(engine, str(uuid.uuid4())) is None


def test_get_project_returns_project(engine, project_id):
    project = get_project(engine, project_id)
    assert project is not None
    assert project.id == project_id
    assert project.title == "Test Project"


def test_get_project_returns_empty_relations_when_none(engine, project_id):
    project = get_project(engine, project_id)
    assert project is not None
    assert project.stories == []
    assert project.bugs == []
    assert project.hotfixes == []


def test_get_project_groups_bugs_by_prefix(engine, project_id):
    pid_uuid = uuid.UUID(project_id)
    with Session(engine) as session:
        session.add(TaskRow(
            id=uuid.uuid4(), seq=1, project_id=pid_uuid,
            title="Bug", description="d", status=Status.TODO, prefix="b",
        ))
        session.add(TaskRow(
            id=uuid.uuid4(), seq=2, project_id=pid_uuid,
            title="Hotfix", description="d", status=Status.TODO, prefix="h",
        ))
        session.commit()
    project = get_project(engine, project_id)
    assert project is not None
    assert len(project.bugs) == 1
    assert len(project.hotfixes) == 1
    assert project.bugs[0].title == "Bug"
    assert project.hotfixes[0].title == "Hotfix"


def test_get_project_orders_stories_by_seq(engine, project_id):
    pid_uuid = uuid.UUID(project_id)
    with Session(engine) as session:
        for seq in [3, 1, 2]:
            session.add(StoryRow(
                id=uuid.uuid4(), seq=seq, project_id=pid_uuid,
                title=f"Story {seq}", description="d", status=Status.TODO,
            ))
        session.commit()
    project = get_project(engine, project_id)
    assert project is not None
    assert [s.seq for s in project.stories] == [1, 2, 3]


def test_get_project_orders_bugs_by_seq(engine, project_id):
    pid_uuid = uuid.UUID(project_id)
    with Session(engine) as session:
        for seq in [3, 1, 2]:
            session.add(TaskRow(
                id=uuid.uuid4(), seq=seq, project_id=pid_uuid,
                title=f"Bug {seq}", description="d", status=Status.TODO, prefix="b",
            ))
        session.commit()
    project = get_project(engine, project_id)
    assert project is not None
    assert [b.seq for b in project.bugs] == [1, 2, 3]
