from pydantic import BaseModel


class StepIngest(BaseModel):
    title: str
    description: str


class TaskIngest(BaseModel):
    title: str
    description: str
    steps: list[StepIngest] = []


class StoryIngest(BaseModel):
    title: str
    description: str
    tasks: list[TaskIngest] = []


class ProjectIngest(BaseModel):
    title: str
    description: str
    stories: list[StoryIngest] = []
    bugs: list[TaskIngest] = []
    hotfixes: list[TaskIngest] = []
