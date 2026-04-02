from db.models import Story, StoryCreate, StoryUpdate
from db.repo import create_story, get_project, get_story, get_story_by_seq, list_active_stories, update_story
from sqlalchemy.engine import Engine

from .exceptions import NotFound


def list_stories(project_id: str, engine: Engine) -> list[Story]:
    """Return all active stories for the given project.

    Args:
        project_id: UUID of the project.
        engine: SQLAlchemy engine.

    Returns:
        List of active Story objects belonging to the project.

    Raises:
        NotFound: If the project does not exist.
    """
    project = get_project(engine, project_id=project_id)
    if project is None:
        raise NotFound(f"Project {project_id} not found")
    return list_active_stories(engine, project_id=project_id)


def get_story_by_id(story_id: str, engine: Engine) -> Story:
    """Fetch a story by its UUID.

    Args:
        story_id: UUID of the story.
        engine: SQLAlchemy engine.

    Returns:
        The matching Story.

    Raises:
        NotFound: If no story with the given ID exists.
    """
    story = get_story(engine, story_id=story_id)
    if story is None:
        raise NotFound(f"Story {story_id} not found")
    return story


def get_story_by_project_seq(project_id: str, seq: int, engine: Engine) -> Story:
    """Fetch a story by its project-scoped sequence number.

    Args:
        project_id: UUID of the project the story belongs to.
        seq: Project-scoped sequence number of the story.
        engine: SQLAlchemy engine.

    Returns:
        The matching Story.

    Raises:
        NotFound: If no story with the given sequence number exists in the project.
    """
    story = get_story_by_seq(engine, project_id=project_id, seq=seq)
    if story is None:
        raise NotFound(f"Story {seq} not found in project {project_id}")
    return story


def create_story_for_project(data: StoryCreate, engine: Engine) -> Story:
    """Create a new story under the project specified in data.

    Args:
        data: Story creation payload including project_id, title, and description.
        engine: SQLAlchemy engine.

    Returns:
        The newly created Story.
    """
    return create_story(engine, data=data)


def update_story_by_id(story_id: str, data: StoryUpdate, engine: Engine) -> Story:
    """Apply partial updates to the story with the given ID.

    Args:
        story_id: UUID of the story to update.
        data: Fields to update; None values are ignored.
        engine: SQLAlchemy engine.

    Returns:
        The updated Story.

    Raises:
        NotFound: If no story with the given ID exists.
    """
    story = update_story(engine, story_id=story_id, data=data)
    if story is None:
        raise NotFound(f"Story {story_id} not found")
    return story
