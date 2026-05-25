from datetime import datetime

from pydantic import BaseModel

from .dod import DoDItem
from .step import Step
from .utils import Status


class Task(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    definition_of_done: list[DoDItem] | None = None
    prefix: str | None
    status: Status
    story_id: str | None = None
    steps: list[Step] = []
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    definition_of_done: list[DoDItem] | None = None
    story_id: str | None = None
    prefix: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    definition_of_done: list[DoDItem] | None = None
    status: Status | None = None
    prefix: str | None = None
