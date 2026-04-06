import typer

from db.models import StoryCreate, StoryUpdate, Status

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json, print_list
from ..services.exceptions import NotFound
from ..services.stories import (
    create_story_for_project,
    get_story_by_id,
    get_story_by_project_seq,
    list_stories,
    update_story_by_id,
)

app = typer.Typer(no_args_is_help=True)


def _is_uuid(value: str) -> bool:
    import uuid

    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


@app.command("list")
def list_cmd(project: str = typer.Option(..., "--project", help="Project ID")) -> None:
    """List all active stories for a project.

    Args:
        project: UUID of the project.
    """
    engine = get_engine()
    try:
        stories = list_stories(project, engine)
        print_list(stories)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("get")
def get(
    id_or_seq: str,
    project: str | None = typer.Option(
        None, "--project", help="Project ID (required for seq lookup)"
    ),
) -> None:
    """Fetch a story by UUID or sequence number and print it as JSON.

    Args:
        id_or_seq: UUID of the story, or its project-scoped sequence number.
        project: Project UUID — required when id_or_seq is a sequence number.
    """
    engine = get_engine()
    try:
        if _is_uuid(id_or_seq):
            story = get_story_by_id(id_or_seq, engine)
        else:
            if project is None:
                raise typer.BadParameter(
                    "--project is required when using a sequence number"
                )
            story = get_story_by_project_seq(project, int(id_or_seq), engine)
        print_json(story)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("create")
def create(
    project: str = typer.Option(..., "--project", help="Project ID"),
    title: str = typer.Option(..., "--title"),
    description: str = typer.Option(..., "--description"),
) -> None:
    """Create a new story under a project and print it as JSON.

    Args:
        project: UUID of the project.
        title: Story title.
        description: Story description.
    """
    engine = get_engine()
    try:
        story = create_story_for_project(
            StoryCreate(project_id=project, title=title, description=description),
            engine,
        )
        print_json(story)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("update")
def update(
    id: str,
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
    status: str | None = typer.Option(None, "--status"),
) -> None:
    """Update fields on a story and print the result as JSON.

    Args:
        id: UUID of the story to update.
        title: New title, if updating.
        description: New description, if updating.
        status: New status value, if updating.
    """
    engine = get_engine()
    try:
        data = StoryUpdate(
            title=title,
            description=description,
            status=Status(status) if status else None,
        )
        story = update_story_by_id(id, data, engine)
        print_json(story)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
