from typing import Annotated

import typer

import db.repo as repo

from ..db import get_engine
from ..errors import NotFoundError
from ..output import confirm, console

app = typer.Typer(name="tasks", no_args_is_help=True)


@app.command("delete")
def delete(
    task_id: Annotated[str, typer.Argument()],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    task = repo.get_task(engine, task_id)
    if not task:
        raise NotFoundError(f"Task {task_id} not found")
    step_count = len(task.steps)
    console.print(
        f"Will delete task [bold]{task.title}[/bold] ({task_id})\n  Steps: {step_count}"
    )
    if not confirm("Proceed with deletion?", force):
        raise typer.Abort()
    repo.delete_task(engine, task_id)
    console.print(f"[green]Deleted task {task_id}[/green]")
