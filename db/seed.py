"""Seed the database from gui/examples/sample_project.json."""

import json
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from db.engine import create_db_engine
from db.orm import Completion, Project, Step, Story, Task

EXAMPLES_DIR = Path(__file__).parent.parent / "gui" / "examples"


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def seed(session: Session, data: dict) -> None:
    project = Project(
        id=uuid.UUID(data["id"]),
        title=data["title"],
        description=data["description"],
        status=data["status"],
        created_at=_dt(data["created_at"]),
        updated_at=_dt(data["updated_at"]),
    )
    session.add(project)

    for s in data["stories"]:
        story = Story(
            id=uuid.UUID(s["id"]),
            project_id=project.id,
            seq=s["seq"],
            title=s["title"],
            description=s["description"],
            status=s["status"],
            created_at=_dt(s["created_at"]),
            updated_at=_dt(s["updated_at"]),
        )
        session.add(story)

        for t in s["tasks"]:
            task = Task(
                id=uuid.UUID(t["id"]),
                project_id=project.id,
                story_id=story.id,
                seq=t["seq"],
                prefix=t["prefix"],
                title=t["title"],
                description=t["description"],
                status=t["status"],
                created_at=_dt(t["created_at"]),
                updated_at=_dt(t["updated_at"]),
            )
            session.add(task)

            for st in t["steps"]:
                session.add(Step(
                    id=uuid.UUID(st["id"]),
                    task_id=task.id,
                    seq=st["seq"],
                    title=st["title"],
                    description=st["description"],
                    status=st["status"],
                    created_at=_dt(st["created_at"]),
                    updated_at=_dt(st["updated_at"]),
                ))

    for t in data.get("bugs", []) + data.get("hotfixes", []):
        task = Task(
            id=uuid.UUID(t["id"]),
            project_id=project.id,
            story_id=None,
            seq=t["seq"],
            prefix=t["prefix"],
            title=t["title"],
            description=t["description"],
            status=t["status"],
            created_at=_dt(t["created_at"]),
            updated_at=_dt(t["updated_at"]),
        )
        session.add(task)

        for st in t["steps"]:
            session.add(Step(
                id=uuid.UUID(st["id"]),
                task_id=task.id,
                seq=st["seq"],
                title=st["title"],
                description=st["description"],
                status=st["status"],
                created_at=_dt(st["created_at"]),
                updated_at=_dt(st["updated_at"]),
            ))

    for c in data.get("completions", []):
        session.add(Completion(
            id=uuid.UUID(c["id"]),
            entity_type=c["entity_type"],
            entity_id=uuid.UUID(c["entity_id"]),
            action=c["action"],
            agent_name=c["agent_name"],
            session_id=c["session_id"],
            branch=c.get("branch"),
            created_at=_dt(c["created_at"]),
            updated_at=_dt(c["updated_at"]),
        ))


def main() -> None:
    engine = create_db_engine()
    with Session(engine) as session:
        for path in sorted(EXAMPLES_DIR.glob("*.json")):
            data = json.loads(path.read_text())
            seed(session, data)
            print(f"Seeded project: {data['title']}")
        session.commit()


if __name__ == "__main__":
    main()
