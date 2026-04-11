import typer

from db.models import Status, TaskCreate, TaskUpdate

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json, print_list
from ..services.exceptions import InvalidStatus, NotFound
from ._input import resolve_description
from ..services.tasks import (
    complete_task,
    create_task_for_story,
    get_floating_task_by_project_seq,
    get_task_by_id,
    get_task_by_story_seq,
    list_floating_tasks_for_project,
    start_task,
    update_task_by_id,
)

app = typer.Typer(no_args_is_help=True)


def _is_uuid(value: str) -> bool:
    import uuid

    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


@app.command("get")
def get(
    id_or_seq: str,
    story: str | None = typer.Option(
        None, "--story", help="Story ID (required for seq lookup)"
    ),
    project: str | None = typer.Option(
        None, "--project", help="Project ID (for floating task seq lookup)"
    ),
) -> None:
    """Fetch a task by UUID or sequence number and print it as JSON.

    Args:
        id_or_seq: UUID of the task, or its sequence number within a story or project.
        story: Story UUID — required when id_or_seq is a sequence number for a story task.
        project: Project UUID — required when id_or_seq is a sequence number for a floating task.
    """
    engine = get_engine()
    try:
        if _is_uuid(id_or_seq):
            task = get_task_by_id(id_or_seq, engine)
        elif story:
            task = get_task_by_story_seq(story, int(id_or_seq), engine)
        elif project:
            task = get_floating_task_by_project_seq(project, int(id_or_seq), engine)
        else:
            raise typer.BadParameter(
                "--story or --project is required when using a sequence number"
            )

        print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("list-floating")
def list_floating(
    project: str = typer.Option(..., "--project", help="Project ID"),
) -> None:
    """List all floating (story-less) tasks for a project and print them as JSON.

    Args:
        project: UUID of the project.
    """
    engine = get_engine()
    try:
        tasks = list_floating_tasks_for_project(project, engine)
        print_list(tasks)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("create")
def create(
    story: str | None = typer.Option(None, "--story", help="Story ID"),
    project: str | None = typer.Option(
        None, "--project", help="Project ID (for floating tasks)"
    ),
    prefix: str | None = typer.Option(
        None, "--prefix", help="Prefix for floating tasks (b=bug, h=hotfix)"
    ),
    title: str = typer.Option(..., "--title"),
    description: str | None = typer.Option(None, "--description"),
    description_file: str | None = typer.Option(
        None, "--description-file", help="Path to a file containing the description"
    ),
) -> None:
    """Create a new task under a story or as a floating task under a project.

    Args:
        story: Story UUID — use for story-linked tasks. Mutually exclusive with project.
        project: Project UUID — use for floating tasks not linked to a story.
        prefix: Short prefix to categorise the floating task (e.g. b=bug, h=hotfix).
        title: Task title.
        description: Task description.
        description_file: Path to a file containing the task description.
    """
    engine = get_engine()
    try:
        if story is None and project is None:
            raise typer.BadParameter("--story or --project is required")
        description_text = resolve_description(description, description_file)
        if description_text is None:
            raise typer.BadParameter("--description or --description-file is required")
        data = TaskCreate(
            story_id=story,
            project_id=project or "",
            prefix=prefix,
            title=title,
            description=description_text,
        )
        task = create_task_for_story(data, engine)
        print_json(task)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("update")
def update(
    id: str,
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
    description_file: str | None = typer.Option(
        None, "--description-file", help="Path to a file containing the description"
    ),
    status: str | None = typer.Option(None, "--status"),
    prefix: str | None = typer.Option(None, "--prefix"),
) -> None:
    """Update fields on a task and print the result as JSON.

    Args:
        id: UUID of the task to update.
        title: New title, if updating.
        description: New description, if updating.
        description_file: Path to a file containing the new description.
        status: New status value, if updating.
        prefix: New prefix, if updating.
    """
    engine = get_engine()
    try:
        description_text = resolve_description(description, description_file)
        data = TaskUpdate(
            title=title,
            description=description_text,
            status=Status(status) if status else None,
            prefix=prefix,
        )
        task = update_task_by_id(id, data, engine)
        print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("start")
def start(
    id: str,
    agent: str = typer.Option(..., "--agent", help="Agent name"),
    session: str = typer.Option(..., "--session", help="Session ID"),
    branch: str | None = typer.Option(None, "--branch", help="Git branch"),
) -> None:
    engine = get_engine()
    try:
        task = start_task(id, agent, session, branch, engine)
        print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except InvalidStatus as e:
        exit_user_error("invalid_status", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("complete")
def complete(
    id: str,
    agent: str = typer.Option(..., "--agent", help="Agent name"),
    session: str = typer.Option(..., "--session", help="Session ID"),
    branch: str | None = typer.Option(None, "--branch", help="Git branch"),
) -> None:
    engine = get_engine()
    try:
        task = complete_task(id, agent, session, branch, engine)
        print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except InvalidStatus as e:
        exit_user_error("invalid_status", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
