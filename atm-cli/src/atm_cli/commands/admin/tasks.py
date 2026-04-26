import pathlib
import subprocess
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


def _render_task_md(task, story=None) -> str:
    lines: list[str] = []
    if story is not None:
        lines += [
            f"## Story [{story.seq}] {story.title}",
            "",
            story.description or "",
            "",
        ]
    lines += [
        f"# [{task.seq}] {task.title}",
        "",
        f"- **ID:** {task.id}",
        f"- **Status:** {STATUS_LABEL.get(task.status, task.status)}",
        "",
        task.description or "",
    ]
    if task.definition_of_done:
        lines += ["", f"**Definition of Done:** {task.definition_of_done}"]
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
            if step.definition_of_done:
                lines += ["", f"**Definition of Done:** {step.definition_of_done}"]
    return "\n".join(lines)


@app.command("dispatch")
def dispatch(
    task_id: Annotated[str, typer.Argument()],
    worktree: Annotated[bool, typer.Option("--worktree")] = False,
    output: Annotated[str | None, typer.Option("--output")] = None,
) -> None:
    engine = get_engine()
    task = repo.get_task(engine, task_id)
    if not task:
        raise NotFoundError(f"Task {task_id} not found")
    story = repo.get_story(engine, str(task.story_id)) if task.story_id else None
    md = _render_task_md(task, story)
    if worktree:
        repo_root = pathlib.Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], text=True
            ).strip()
        )
        wt_path = repo_root.parent / f"{repo_root.name}-task-{task.seq}"
        branch = f"task/{task.seq}"
        subprocess.run(
            ["git", "worktree", "add", str(wt_path), "-b", branch], check=True
        )
        plan_path = wt_path / "plan.md"
        plan_path.write_text(md)
        console.print(f"[green]Dispatched task {task_id} to {wt_path}[/green]")
    elif output:
        with open(output, "w") as f:
            f.write(md)
        console.print(f"[green]Wrote task {task_id} to {output}[/green]")
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
