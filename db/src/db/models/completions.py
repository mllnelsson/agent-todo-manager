from datetime import datetime

from pydantic import BaseModel

from .utils import Action, EntityType


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
