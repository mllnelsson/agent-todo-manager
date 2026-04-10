from typing import Annotated

import typer

import db.repo as repo
from db.repo.queries import (
    list_orphaned_tasks,
    list_stale_steps,
    list_stale_tasks,
    list_todo_in_completed_stories,
)

from ...db import get_engine
from .output import confirm, console, print_table

app = typer.Typer(name="prune", no_args_is_help=True)


@app.command("stale")
def stale(
    project_id: Annotated[str, typer.Option("--project")],
    days: Annotated[int, typer.Option("--days")] = 7,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    stale_tasks = list_stale_tasks(engine, project_id, days)
    stale_steps = list_stale_steps(engine, project_id, days)

    if not stale_tasks and not stale_steps:
        console.print(f"No stale items found (>{days} days, not completed).")
        return

    if stale_tasks:
        print_table(
            f"Stale Tasks (>{days} days)",
            ["ID", "Title", "Status", "Updated"],
            [
                [t.id, t.title, t.status, t.updated_at.strftime("%Y-%m-%d")]
                for t in stale_tasks
            ],
        )
    if stale_steps:
        print_table(
            f"Stuck Steps (IN_PROGRESS >{days} days)",
            ["ID", "Title", "Updated"],
            [[s.id, s.title, s.updated_at.strftime("%Y-%m-%d")] for s in stale_steps],
        )

    if not confirm("Delete these items?", force):
        raise typer.Abort()

    for task in stale_tasks:
        repo.delete_task(engine, task.id)
    for step in stale_steps:
        repo.delete_step(engine, step.id)
    console.print(
        f"[green]Deleted {len(stale_tasks)} tasks and {len(stale_steps)} steps.[/green]"
    )


@app.command("stuck")
def stuck(
    project_id: Annotated[str, typer.Option("--project")],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    steps = list_stale_steps(engine, project_id, days=0)

    if not steps:
        console.print("No stuck steps found.")
        return

    print_table(
        "Stuck Steps (IN_PROGRESS)",
        ["ID", "Title", "Updated"],
        [[s.id, s.title, s.updated_at.strftime("%Y-%m-%d")] for s in steps],
    )

    if not confirm("Delete these steps?", force):
        raise typer.Abort()

    for step in steps:
        repo.delete_step(engine, step.id)
    console.print(f"[green]Deleted {len(steps)} stuck steps.[/green]")


@app.command("dirty")
def dirty(
    project_id: Annotated[str, typer.Option("--project")],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    orphaned = list_orphaned_tasks(engine, project_id)
    todo_in_completed = list_todo_in_completed_stories(engine, project_id)

    if not orphaned and not todo_in_completed:
        console.print("No dirty state found.")
        return

    if orphaned:
        print_table(
            "Orphaned Tasks (not COMPLETED in COMPLETED story)",
            ["ID", "Title", "Status"],
            [[t.id, t.title, t.status] for t in orphaned],
        )
    if todo_in_completed:
        print_table(
            "TODO Tasks in COMPLETED Stories (never started)",
            ["ID", "Title", "Status"],
            [[t.id, t.title, t.status] for t in todo_in_completed],
        )

    all_dirty = orphaned + todo_in_completed
    if not confirm(f"Delete {len(all_dirty)} dirty entities?", force):
        raise typer.Abort()

    for task in all_dirty:
        repo.delete_task(engine, task.id)
    console.print(f"[green]Deleted {len(all_dirty)} dirty tasks.[/green]")
