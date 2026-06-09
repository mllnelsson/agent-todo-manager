import json

import typer

from db.models import StepCreate, StepUpdate

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json
from ..services.exceptions import NotFound, ProjectArchived
from ._input import resolve_description
from ..services.steps import (
    create_step_for_task,
    delete_step_by_task_seq,
    get_step_by_task_seq,
    update_step_by_id,
)

app = typer.Typer(no_args_is_help=True)


@app.command("get")
def get(
    seq: int,
    task: str = typer.Option(..., "--task", help="Task ID"),
) -> None:
    """Fetch a step by its task-scoped sequence number and print it as JSON.

    Args:
        seq: Task-scoped sequence number of the step.
        task: UUID of the parent task.
    """
    engine = get_engine()
    try:
        step = get_step_by_task_seq(task, seq, engine)
        print_json(step)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("create")
def create(
    task: str = typer.Option(..., "--task", help="Task ID"),
    title: str = typer.Option(..., "--title"),
    description: str | None = typer.Option(None, "--description"),
    description_file: str | None = typer.Option(
        None, "--description-file", help="Path to a file containing the description"
    ),
) -> None:
    """Create a new step under a task and print it as JSON.

    Args:
        task: UUID of the parent task.
        title: Step title.
        description: Step description.
        description_file: Path to a file containing the step description.
    """
    engine = get_engine()
    try:
        description_text = resolve_description(description, description_file)
        if description_text is None:
            raise typer.BadParameter("--description or --description-file is required")
        step = create_step_for_task(
            StepCreate(
                task_id=task,
                title=title,
                description=description_text,
            ),
            engine,
        )
        print_json(step)
    except ProjectArchived as e:
        exit_user_error("project_archived", str(e))
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
) -> None:
    """Update fields on a step and print the result as JSON.

    Args:
        id: UUID of the step to update.
        title: New title, if updating.
        description: New description, if updating.
        description_file: Path to a file containing the new description.
    """
    engine = get_engine()
    try:
        description_text = resolve_description(description, description_file)
        step = update_step_by_id(
            id,
            StepUpdate(title=title, description=description_text),
            engine,
        )
        print_json(step)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except ProjectArchived as e:
        exit_user_error("project_archived", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("delete")
def delete(
    seq: int,
    task: str = typer.Option(..., "--task", help="Task ID"),
) -> None:
    """Delete a step by its task-scoped sequence number and print a confirmation as JSON."""
    engine = get_engine()
    try:
        delete_step_by_task_seq(task, seq, engine)
        print(json.dumps({"deleted": "step", "task_id": task, "seq": seq}))
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except ProjectArchived as e:
        exit_user_error("project_archived", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
