import uuid

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from db.models import Project, ProjectCreate, ProjectUpdate, Status
from db.orm import Project as ProjectRow


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


def get_project(engine: Engine, project_id: str) -> Project | None:
    with Session(engine) as session:
        row = session.get(ProjectRow, uuid.UUID(project_id))
        return _to_model(row) if row else None


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


def update_project(
    engine: Engine, project_id: str, data: ProjectUpdate
) -> Project | None:
    with Session(engine) as session:
        row = session.get(ProjectRow, uuid.UUID(project_id))
        if not row:
            return None
        if data.title is not None:
            row.title = data.title
        if data.description is not None:
            row.description = data.description
        if data.status is not None:
            row.status = data.status
        session.commit()
        session.refresh(row)
        return _to_model(row)


def delete_project(engine: Engine, project_id: str) -> bool:
    with Session(engine) as session:
        row = session.get(ProjectRow, uuid.UUID(project_id))
        if not row:
            return False
        session.delete(row)
        session.commit()
        return True
