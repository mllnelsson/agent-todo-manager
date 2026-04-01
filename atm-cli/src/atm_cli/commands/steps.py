import typer

from db.models import StepCreate, StepUpdate

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json
from ..services.exceptions import InvalidStatus, NotFound
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
    description: str = typer.Option(..., "--description"),
) -> None:
    engine = get_engine()
    try:
        step = create_step_for_task(StepCreate(task_id=task, title=title, description=description), engine)
        print_json(step)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("update")
def update(
    id: str,
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    engine = get_engine()
    try:
        step = update_step_by_id(id, StepUpdate(title=title, description=description), engine)
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
