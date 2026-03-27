import uuid

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session, selectinload

from db.models import Project, Status, Step, Story, Task
from db.orm import Project as ProjectRow
from db.orm import Step as StepRow
from db.orm import Story as StoryRow
from db.orm import Task as TaskRow


def _step_to_model(row: StepRow) -> Step:
    return Step(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        status=Status(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _task_to_model(row: TaskRow) -> Task:
    return Task(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        prefix=row.prefix,
        status=Status(row.status),
        steps=sorted([_step_to_model(s) for s in row.steps], key=lambda s: s.seq),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _story_to_model(row: StoryRow) -> Story:
    return Story(
        id=str(row.id),
        seq=row.seq,
        title=row.title,
        description=row.description,
        status=Status(row.status),
        tasks=sorted([_task_to_model(t) for t in row.tasks], key=lambda t: t.seq),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_model(row: ProjectRow) -> Project:
    return Project(
        id=str(row.id),
        title=row.title,
        description=row.description,
        status=Status(row.status),
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def get_project(engine: Engine, project_id: str) -> Project | None:
    with Session(engine) as session:
        stmt = (
            select(ProjectRow)
            .where(ProjectRow.id == uuid.UUID(project_id))
            .options(
                selectinload(ProjectRow.stories)
                .selectinload(StoryRow.tasks)
                .selectinload(TaskRow.steps),
                selectinload(ProjectRow.tasks).selectinload(TaskRow.steps),
            )
        )
        row = session.execute(stmt).scalar_one_or_none()
        if not row:
            return None

        stories = sorted([_story_to_model(s) for s in row.stories], key=lambda s: s.seq)
        floating = [t for t in row.tasks if t.story_id is None]
        bugs = sorted([_task_to_model(t) for t in floating if t.prefix == "b"], key=lambda t: t.seq)
        hotfixes = sorted([_task_to_model(t) for t in floating if t.prefix == "h"], key=lambda t: t.seq)

        return Project(
            id=str(row.id),
            title=row.title,
            description=row.description,
            status=Status(row.status),
            stories=stories,
            bugs=bugs,
            hotfixes=hotfixes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


def list_projects(engine: Engine) -> list[Project]:
    with Session(engine) as session:
        rows = session.execute(select(ProjectRow)).scalars().all()
        return [_to_model(r) for r in rows]


def list_active_projects(engine: Engine) -> list[Project]:
    """Projects not yet completed."""
    with Session(engine) as session:
        stmt = select(ProjectRow).where(ProjectRow.status != Status.COMPLETED)
        rows = session.execute(stmt).scalars().all()
        return [_to_model(r) for r in rows]
