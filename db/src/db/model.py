from pydantic import BaseModel


class Project(BaseModel):
    id: str
    name: str
    description: str


class Task(BaseModel):
    id: str
