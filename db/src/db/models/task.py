from datetime import datetime

from pydantic import BaseModel

from .step import Step
from .utils import Status


class Task(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    definition_of_done: str | None = None
    prefix: str | None
    status: Status
    steps: list[Step] = []
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    definition_of_done: str | None = None
    story_id: str | None = None
    prefix: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    definition_of_done: str | None = None
    status: Status | None = None
    prefix: str | None = None
