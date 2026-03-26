from datetime import datetime

from pydantic import BaseModel

from .utils import Status


class Step(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    status: Status
    created_at: datetime
    updated_at: datetime


class StepCreate(BaseModel):
    task_id: str
    title: str
    description: str


class StepUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None
