from typing import Annotated

import typer

import db.repo as repo
from db.models import Status

from ...db import get_engine
from .errors import NotFoundError
from .output import confirm, console

app = typer.Typer(name="tasks", no_args_is_help=True)

STATUS_LABEL = {
    Status.TODO: "TODO",
    Status.IN_PROGRESS: "IN_PROGRESS",
    Status.COMPLETED: "COMPLETED",
}


def _render_task_md(task) -> str:
    lines = [
        f"# [{task.seq}] {task.title}",
        "",
        f"- **ID:** {task.id}",
        f"- **Status:** {STATUS_LABEL.get(task.status, task.status)}",
        "",
        task.description or "",
    ]
    if task.steps:
        lines += ["", "## Steps"]
        for step in task.steps:
            lines += [
                "",
                f"### Step {step.seq}: {step.title}",
                f"- **ID:** {step.id}",
                f"- **Status:** {STATUS_LABEL.get(step.status, step.status)}",
                "",
                step.description or "",
            ]
    return "\n".join(lines)


@app.command("export")
def export(
    task_id: Annotated[str, typer.Argument()],
    output: Annotated[str | None, typer.Option("--output")] = None,
) -> None:
    engine = get_engine()
    task = repo.get_task(engine, task_id)
    if not task:
        raise NotFoundError(f"Task {task_id} not found")
    md = _render_task_md(task)
    if output:
        with open(output, "w") as f:
            f.write(md)
        console.print(f"[green]Exported task {task_id} to {output}[/green]")
    else:
        print(md)


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
