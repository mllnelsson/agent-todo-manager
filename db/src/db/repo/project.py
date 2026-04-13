import uuid

from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session, selectinload

from db.models import Project, ProjectCreate, Status, Step, Story, Task
from db.models.ingest import ProjectIngest
from db.orm import Completion as CompletionRow
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
        definition_of_done=row.definition_of_done,
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
        definition_of_done=row.definition_of_done,
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


def create_project(engine: Engine, data: ProjectCreate) -> Project:
    with Session(engine) as session:
        row = ProjectRow(
            id=uuid.uuid4(),
            title=data.title,
            description=data.description,
            status=Status.TODO,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return _to_model(row)


def delete_project(engine: Engine, project_id: str) -> bool:
    pid = uuid.UUID(project_id)
    with Session(engine) as session:
        row = session.get(ProjectRow, pid)
        if not row:
            return False
        story_ids = [
            r.id
            for r in session.execute(
                select(StoryRow.id).where(StoryRow.project_id == pid)
            ).all()
        ]
        task_ids = [
            r.id
            for r in session.execute(
                select(TaskRow.id).where(TaskRow.project_id == pid)
            ).all()
        ]
        step_ids = []
        if task_ids:
            step_ids = [
                r.id
                for r in session.execute(
                    select(StepRow.id).where(StepRow.task_id.in_(task_ids))
                ).all()
            ]
        entity_ids = [pid] + story_ids + task_ids + step_ids
        session.execute(
            delete(CompletionRow).where(CompletionRow.entity_id.in_(entity_ids))
        )
        if step_ids:
            session.execute(delete(StepRow).where(StepRow.id.in_(step_ids)))
        if task_ids:
            session.execute(delete(TaskRow).where(TaskRow.id.in_(task_ids)))
        if story_ids:
            session.execute(delete(StoryRow).where(StoryRow.id.in_(story_ids)))
        session.delete(row)
        session.commit()
        return True


def ingest_project(engine: Engine, data: ProjectIngest) -> Project:
    with Session(engine) as session:
        project_id = uuid.uuid4()
        project_row = ProjectRow(
            id=project_id,
            title=data.title,
            description=data.description,
            status=Status.TODO,
        )
        session.add(project_row)

        for story_seq, story_data in enumerate(data.stories, start=1):
            story_id = uuid.uuid4()
            story_row = StoryRow(
                id=story_id,
                seq=story_seq,
                project_id=project_id,
                title=story_data.title,
                description=story_data.description,
                status=Status.TODO,
            )
            session.add(story_row)
            for task_seq, task_data in enumerate(story_data.tasks, start=1):
                task_id = uuid.uuid4()
                task_row = TaskRow(
                    id=task_id,
                    seq=task_seq,
                    project_id=project_id,
                    story_id=story_id,
                    prefix=None,
                    title=task_data.title,
                    description=task_data.description,
                    definition_of_done=task_data.definition_of_done,
                    status=Status.TODO,
                )
                session.add(task_row)
                for step_seq, step_data in enumerate(task_data.steps, start=1):
                    step_row = StepRow(
                        id=uuid.uuid4(),
                        seq=step_seq,
                        task_id=task_id,
                        title=step_data.title,
                        description=step_data.description,
                        definition_of_done=step_data.definition_of_done,
                        status=Status.TODO,
                    )
                    session.add(step_row)

        for prefix, floating_list in (("b", data.bugs), ("h", data.hotfixes)):
            for task_seq, task_data in enumerate(floating_list, start=1):
                task_id = uuid.uuid4()
                task_row = TaskRow(
                    id=task_id,
                    seq=task_seq,
                    project_id=project_id,
                    story_id=None,
                    prefix=prefix,
                    title=task_data.title,
                    description=task_data.description,
                    definition_of_done=task_data.definition_of_done,
                    status=Status.TODO,
                )
                session.add(task_row)
                for step_seq, step_data in enumerate(task_data.steps, start=1):
                    step_row = StepRow(
                        id=uuid.uuid4(),
                        seq=step_seq,
                        task_id=task_id,
                        title=step_data.title,
                        description=step_data.description,
                        definition_of_done=step_data.definition_of_done,
                        status=Status.TODO,
                    )
                    session.add(step_row)

        session.commit()
        session.refresh(project_row)
        return get_project(engine, str(project_id))  # type: ignore[return-value]


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
        bugs = sorted(
            [_task_to_model(t) for t in floating if t.prefix == "b"],
            key=lambda t: t.seq,
        )
        hotfixes = sorted(
            [_task_to_model(t) for t in floating if t.prefix == "h"],
            key=lambda t: t.seq,
        )

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
