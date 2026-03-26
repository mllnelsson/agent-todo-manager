from datetime import datetime

from pydantic import BaseModel

from .story import Story
from .task import Task
from .utils import Status


class Project(BaseModel):
    id: str
    title: str
    description: str
    status: Status
    stories = list[Story]
    bugs = list[Task]
    hotfixes = list[Task]
    created_at: datetime
    updated_at: datetime


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None
