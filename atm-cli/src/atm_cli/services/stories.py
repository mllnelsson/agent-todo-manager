from db.models import Story, StoryCreate, StoryUpdate
from db.repo import create_story, get_project, get_story, get_story_by_seq, list_active_stories, update_story
from sqlalchemy.engine import Engine

from .exceptions import NotFound


def list_stories(project_id: str, engine: Engine) -> list[Story]:
    project = get_project(engine, project_id=project_id)
    if project is None:
        raise NotFound(f"Project {project_id} not found")
    return list_active_stories(engine, project_id=project_id)


def get_story_by_id(story_id: str, engine: Engine) -> Story:
    story = get_story(engine, story_id=story_id)
    if story is None:
        raise NotFound(f"Story {story_id} not found")
    return story


def get_story_by_project_seq(project_id: str, seq: int, engine: Engine) -> Story:
    story = get_story_by_seq(engine, project_id=project_id, seq=seq)
    if story is None:
        raise NotFound(f"Story {seq} not found in project {project_id}")
    return story


def create_story_for_project(data: StoryCreate, engine: Engine) -> Story:
    return create_story(engine, data=data)


def update_story_by_id(story_id: str, data: StoryUpdate, engine: Engine) -> Story:
    story = update_story(engine, story_id=story_id, data=data)
    if story is None:
        raise NotFound(f"Story {story_id} not found")
    return story
