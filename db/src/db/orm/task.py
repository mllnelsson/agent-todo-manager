import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .step import Step
    from .story import Story


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
    description: Mapped[str] = mapped_column(Text)
    definition_of_done: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(255))

    steps: Mapped[list["Step"]] = relationship(back_populates="task")
