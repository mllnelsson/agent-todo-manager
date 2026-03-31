from db.models import Story, StoryCreate, StoryUpdate
from db.repo import get_project, get_story
from sqlalchemy import Engine

from .utils import NotFound


def list_stories_by_project_id(project_id: str, engine: Engine) -> list[Story]:
    project = get_project(engine, project_id=project_id)
    if project is None:
        raise NotFound(f"Project {id} not found")
    return project.stories


def get_story_by_id(id: str, engine: Engine) -> Story:
    """TODO: improve this string. This one returns the complete story tree"""
    story = get_story(engine, story_id=id)
    if story is None:
        raise NotFound(f"Story {id} not found")
    return story
