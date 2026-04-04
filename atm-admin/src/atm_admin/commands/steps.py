from typing import Annotated

import typer

import db.repo as repo

from ..db import get_engine
from ..errors import NotFoundError
from ..output import confirm, console

app = typer.Typer(name="steps", no_args_is_help=True)


@app.command("delete")
def delete(
    step_id: Annotated[str, typer.Argument()],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    step = repo.get_step(engine, step_id)
    if not step:
        raise NotFoundError(f"Step {step_id} not found")
    console.print(f"Will delete step [bold]{step.title}[/bold] ({step_id})")
    if not confirm("Proceed with deletion?", force):
        raise typer.Abort()
    repo.delete_step(engine, step_id)
    console.print(f"[green]Deleted step {step_id}[/green]")
