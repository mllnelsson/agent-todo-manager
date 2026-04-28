import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Status
from db.orm import Base
from db.orm import Project as ProjectRow
from db.orm import Story as StoryRow
from db.orm import Task as TaskRow


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def project_id(engine):
    pid = uuid.uuid4()
    with Session(engine) as session:
        session.add(
            ProjectRow(
                id=pid,
                title="Test Project",
                description="A test project",
                status=Status.TODO,
            )
        )
        session.commit()
    return str(pid)


@pytest.fixture
def story_id(engine, project_id):
    sid = uuid.uuid4()
    with Session(engine) as session:
        session.add(
            StoryRow(
                id=sid,
                seq=1,
                project_id=uuid.UUID(project_id),
                title="Test Story",
                description="A test story",
                status=Status.TODO,
            )
        )
        session.commit()
    return str(sid)


def _add_task(engine, project_id, story_id, *, seq, status):
    tid = uuid.uuid4()
    with Session(engine) as session:
        session.add(
            TaskRow(
                id=tid,
                seq=seq,
                project_id=uuid.UUID(project_id),
                story_id=uuid.UUID(story_id),
                title=f"Task {seq}",
                description="A test task",
                status=status,
            )
        )
        session.commit()
    return str(tid)


@pytest.fixture
def make_task(engine, project_id, story_id):
    counter = {"seq": 0}

    def _make(status: Status = Status.TODO) -> str:
        counter["seq"] += 1
        return _add_task(engine, project_id, story_id, seq=counter["seq"], status=status)

    return _make
