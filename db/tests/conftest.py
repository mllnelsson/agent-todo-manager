import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Status
from db.orm import Base
from db.orm import Project as ProjectRow
from db.orm import Step as StepRow
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
        session.add(ProjectRow(
            id=pid,
            title="Test Project",
            description="A test project",
            status=Status.TODO,
        ))
        session.commit()
    return str(pid)


@pytest.fixture
def story_id(engine, project_id):
    sid = uuid.uuid4()
    with Session(engine) as session:
        session.add(StoryRow(
            id=sid,
            seq=1,
            project_id=uuid.UUID(project_id),
            title="Test Story",
            description="A test story",
            status=Status.TODO,
        ))
        session.commit()
    return str(sid)


@pytest.fixture
def task_id(engine, project_id, story_id):
    tid = uuid.uuid4()
    with Session(engine) as session:
        session.add(TaskRow(
            id=tid,
            seq=1,
            project_id=uuid.UUID(project_id),
            story_id=uuid.UUID(story_id),
            title="Test Task",
            description="A test task",
            status=Status.TODO,
        ))
        session.commit()
    return str(tid)


@pytest.fixture
def step_id(engine, task_id):
    sid = uuid.uuid4()
    with Session(engine) as session:
        session.add(StepRow(
            id=sid,
            seq=1,
            task_id=uuid.UUID(task_id),
            title="Test Step",
            description="A test step",
        ))
        session.commit()
    return str(sid)
