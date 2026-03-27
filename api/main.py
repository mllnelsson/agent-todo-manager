from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.engine import Engine

from db.engine import create_db_engine
from db.models import Project
from db.repo import get_project, list_completions_for_entities, list_projects

from models import ProjectDetail


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.engine = create_db_engine()
    yield
    app.state.engine.dispose()


app = FastAPI(lifespan=lifespan)


def get_engine(request: Request) -> Engine:
    return request.app.state.engine


EngineDep = Annotated[Engine, Depends(get_engine)]


def _collect_entity_ids(project: Project) -> list[str]:
    ids: list[str] = []
    for story in project.stories:
        ids.append(story.id)
        for task in story.tasks:
            ids.append(task.id)
            for step in task.steps:
                ids.append(step.id)
    for task in project.bugs + project.hotfixes:
        ids.append(task.id)
        for step in task.steps:
            ids.append(step.id)
    return ids


@app.get("/api/projects")
def list_all_projects(engine: EngineDep) -> list[Project]:
    return list_projects(engine)


@app.get("/api/projects/{project_id}")
def get_project_detail(project_id: str, engine: EngineDep) -> ProjectDetail:
    project = get_project(engine, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    completions = list_completions_for_entities(engine, _collect_entity_ids(project))
    return ProjectDetail(**project.model_dump(), completions=completions)
