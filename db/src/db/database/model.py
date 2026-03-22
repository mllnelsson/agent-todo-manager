import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))

    stories: Mapped[list["Story"]] = relationship(back_populates="project")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")


class Story(TimestampMixin, Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    seq: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="stories")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))

    tasks: Mapped[list["Task"]] = relationship(back_populates="story")


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    seq: Mapped[int] = mapped_column(Integer)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="tasks")
    story_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("stories.id"), nullable=True
    )
    story: Mapped["Story | None"] = relationship(back_populates="tasks")
    prefix: Mapped[str | None] = mapped_column(String(1), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))

    steps: Mapped[list["Step"]] = relationship(back_populates="task")


class Step(TimestampMixin, Base):
    __tablename__ = "steps"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    seq: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped["Task"] = relationship(back_populates="steps")
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255))


class Completion(TimestampMixin, Base):
    __tablename__ = "completions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(255))
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    action: Mapped[str] = mapped_column(String(255))
    agent_name: Mapped[str] = mapped_column(String(255))
    session_id: Mapped[str] = mapped_column(String(255))
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
