from typing import Annotated

import typer

import db.repo as repo

from ..db import get_engine
from ..errors import NotFoundError
from ..output import confirm, console

app = typer.Typer(name="stories", no_args_is_help=True)


@app.command("delete")
def delete(
    story_id: Annotated[str, typer.Argument()],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    story = repo.get_story(engine, story_id)
    if not story:
        raise NotFoundError(f"Story {story_id} not found")
    task_count = len(story.tasks)
    step_count = sum(len(t.steps) for t in story.tasks)
    console.print(
        f"Will delete story [bold]{story.title}[/bold] ({story_id})\n"
        f"  Tasks: {task_count}, Steps: {step_count}"
    )
    if not confirm("Proceed with deletion?", force):
        raise typer.Abort()
    repo.delete_story(engine, story_id)
    console.print(f"[green]Deleted story {story_id}[/green]")
