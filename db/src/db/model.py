from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel


class Status(StrEnum):
    TODO = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class Step(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    status: Status
    created_at: datetime
    updated_at: datetime


class Task(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    prefix: str | None
    status: Status
    steps = list[Step]
    created_at: datetime
    updated_at: datetime


class Story(BaseModel):
    id: str
    seq: int
    title: str
    description: str
    status: Status
    tasks = list[Task]
    created_at: datetime
    updated_at: datetime


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
