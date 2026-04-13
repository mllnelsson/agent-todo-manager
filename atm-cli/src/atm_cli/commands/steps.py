import typer

from db.models import StepCreate, StepUpdate

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json
from ..services.exceptions import InvalidStatus, NotFound
from ._input import resolve_definition_of_done, resolve_description
from ..services.steps import (
    complete_step,
    create_step_for_task,
    get_next_pending_step,
    get_step_by_task_seq,
    start_step,
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


@app.command("next")
def next_cmd(task: str = typer.Option(..., "--task", help="Task ID")) -> None:
    """Fetch the next pending (TODO) step for a task and print it as JSON.

    Args:
        task: UUID of the task.
    """
    engine = get_engine()
    try:
        step = get_next_pending_step(task, engine)
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
    definition_of_done: str | None = typer.Option(None, "--definition-of-done"),
    definition_of_done_file: str | None = typer.Option(
        None,
        "--definition-of-done-file",
        help="Path to a file containing the definition of done",
    ),
) -> None:
    """Create a new step under a task and print it as JSON.

    Args:
        task: UUID of the parent task.
        title: Step title.
        description: Step description.
        description_file: Path to a file containing the step description.
        definition_of_done: Acceptance criteria for the step.
        definition_of_done_file: Path to a file containing the definition of done.
    """
    engine = get_engine()
    try:
        description_text = resolve_description(description, description_file)
        if description_text is None:
            raise typer.BadParameter("--description or --description-file is required")
        dod_text = resolve_definition_of_done(definition_of_done, definition_of_done_file)
        step = create_step_for_task(
            StepCreate(
                task_id=task,
                title=title,
                description=description_text,
                definition_of_done=dod_text,
            ),
            engine,
        )
        print_json(step)
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
    definition_of_done: str | None = typer.Option(None, "--definition-of-done"),
    definition_of_done_file: str | None = typer.Option(
        None,
        "--definition-of-done-file",
        help="Path to a file containing the definition of done",
    ),
) -> None:
    """Update fields on a step and print the result as JSON.

    Args:
        id: UUID of the step to update.
        title: New title, if updating.
        description: New description, if updating.
        description_file: Path to a file containing the new description.
        definition_of_done: New acceptance criteria, if updating.
        definition_of_done_file: Path to a file containing the new definition of done.
    """
    engine = get_engine()
    try:
        description_text = resolve_description(description, description_file)
        dod_text = resolve_definition_of_done(definition_of_done, definition_of_done_file)
        step = update_step_by_id(
            id,
            StepUpdate(title=title, description=description_text, definition_of_done=dod_text),
            engine,
        )
        print_json(step)
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
    """Mark a step as IN_PROGRESS, recording which agent claimed it.

    Args:
        id: UUID of the step to start.
        agent: Name of the agent claiming the step.
        session: Agent session identifier.
        branch: Git branch the agent is working on, if any.
    """
    engine = get_engine()
    try:
        step = start_step(id, agent, session, branch, engine)
        print_json(step)
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
    """Mark a step as COMPLETED, cascading completion to the task and story if applicable.

    Args:
        id: UUID of the step to complete.
        agent: Name of the agent completing the step.
        session: Agent session identifier.
        branch: Git branch the agent worked on, if any.
    """
    engine = get_engine()
    try:
        step = complete_step(id, agent, session, branch, engine)
        print_json(step)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except InvalidStatus as e:
        exit_user_error("invalid_status", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
