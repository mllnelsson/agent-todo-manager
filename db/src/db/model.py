from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel


class Status(StrEnum):
    TODO = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()


class EntityType(StrEnum):
    STORY = auto()
    TASK = auto()
    STEP = auto()


class Action(StrEnum):
    STARTED = auto()
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


# --- DTOs (input models for write operations) ---


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None


class StoryCreate(BaseModel):
    project_id: str
    title: str
    description: str


class StoryUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    story_id: str | None = None
    prefix: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None
    prefix: str | None = None


class StepCreate(BaseModel):
    task_id: str
    title: str
    description: str


class StepUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: Status | None = None


class Completion(BaseModel):
    id: str
    entity_type: EntityType
    entity_id: str
    action: Action
    agent_name: str
    session_id: str
    branch: str | None
    created_at: datetime
    updated_at: datetime


class CompletionCreate(BaseModel):
    entity_type: EntityType
    entity_id: str
    action: Action
    agent_name: str
    session_id: str
    branch: str | None = None
