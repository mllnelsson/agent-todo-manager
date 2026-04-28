from typing import Annotated

import typer

import db.repo as repo
from db.repo.queries import (
    list_orphaned_tasks,
    list_stale_tasks,
    list_todo_in_completed_stories,
)

from ..._env import resolve as resolve_env
from ...db import get_engine
from .output import confirm, console, print_table

app = typer.Typer(name="prune", no_args_is_help=True)


@app.command("stale")
def stale(
    project_id: Annotated[str | None, typer.Option("--project")] = None,
    days: Annotated[int, typer.Option("--days")] = 7,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    project_id = resolve_env(project_id, "ATM_PROJECT_ID", "--project")
    engine = get_engine()
    stale_tasks = list_stale_tasks(engine, project_id, days)

    if not stale_tasks:
        console.print(f"No stale items found (>{days} days, not completed).")
        return

    print_table(
        f"Stale Tasks (>{days} days)",
        ["ID", "Title", "Status", "Updated"],
        [
            [t.id, t.title, t.status, t.updated_at.strftime("%Y-%m-%d")]
            for t in stale_tasks
        ],
    )

    if not confirm("Delete these items?", force):
        raise typer.Abort()

    for task in stale_tasks:
        repo.delete_task(engine, task.id)
    console.print(f"[green]Deleted {len(stale_tasks)} tasks.[/green]")


@app.command("dirty")
def dirty(
    project_id: Annotated[str | None, typer.Option("--project")] = None,
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    project_id = resolve_env(project_id, "ATM_PROJECT_ID", "--project")
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
