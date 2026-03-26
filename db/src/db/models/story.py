from datetime import datetime

from pydantic import BaseModel

from .task import Task
from .utils import Status


class Story(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    status: Status
    tasks = list[Task]
    created_at: datetime
    updated_at: datetime


class StoryCreate(BaseModel):
    project_id: str
    title: str
    description: str


class StoryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None
