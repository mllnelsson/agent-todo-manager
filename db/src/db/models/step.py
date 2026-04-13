from datetime import datetime

from pydantic import BaseModel

from .utils import Status


class Step(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    definition_of_done: str | None = None
    status: Status
    created_at: datetime
    updated_at: datetime


class StepCreate(BaseModel):
    task_id: str
    title: str
    description: str
    definition_of_done: str | None = None


class StepUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    definition_of_done: str | None = None
    status: Status | None = None
