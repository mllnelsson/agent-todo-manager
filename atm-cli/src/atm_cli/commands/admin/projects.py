import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel

import db.repo as repo
from db.models import ProjectCreate
from db.models.ingest import ProjectIngest

from ...db import get_engine
from .errors import NotFoundError
from .output import confirm, console, print_table

app = typer.Typer(name="projects", no_args_is_help=True)


@app.command("create")
def create(
    title: Annotated[str, typer.Option("--title", "-t")],
    description: Annotated[str, typer.Option("--description", "-d")] = "",
    id_file: Annotated[
        Path | None,
        typer.Option(
            "--id-file",
            help="Write the new project ID to this file (non-interactive).",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite an existing --id-file target."),
    ] = False,
) -> None:
    engine = get_engine()
    project = repo.create_project(
        engine, ProjectCreate(title=title, description=description)
    )
    console.print(
        Panel(
            f"[bold]{project.title}[/bold]\n{project.description}\n\nID: {project.id}\nStatus: {project.status}",
            title="Project created",
        )
    )

    if id_file is not None:
        if id_file.exists() and not force:
            raise typer.BadParameter(
                f"{id_file} already exists; pass --force to overwrite"
            )
        _write_id_file(id_file, project.id)
        return

    default_path = Path.cwd() / ".atm_project_id"
    if not confirm(f"Write project ID to {default_path}?", force=False):
        return
    if default_path.exists() and not confirm(
        f"Overwrite existing {default_path}?", force=False
    ):
        return
    _write_id_file(default_path, project.id)


def _write_id_file(path: Path, project_id: str) -> None:
    path.write_text(f"{project_id}\n")
    console.print(f"[green]Wrote project ID to {path}[/green]")


@app.command("list")
def list_projects(
    all: Annotated[bool, typer.Option("--all")] = False,
) -> None:
    engine = get_engine()
    projects = repo.list_projects(engine) if all else repo.list_active_projects(engine)
    print_table(
        "Projects",
        ["ID", "Title", "Status", "Created"],
        [
            [p.id, p.title, p.status, p.created_at.strftime("%Y-%m-%d")]
            for p in projects
        ],
    )


@app.command("delete")
def delete(
    project_id: Annotated[str, typer.Argument()],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    engine = get_engine()
    project = repo.get_project(engine, project_id)
    if not project:
        raise NotFoundError(f"Project {project_id} not found")
    story_count = len(project.stories)
    task_count = (
        sum(len(s.tasks) for s in project.stories)
        + len(project.bugs)
        + len(project.hotfixes)
    )
    step_count = (
        sum(len(t.steps) for s in project.stories for t in s.tasks)
        + sum(len(t.steps) for t in project.bugs)
        + sum(len(t.steps) for t in project.hotfixes)
    )
    console.print(
        f"Will delete project [bold]{project.title}[/bold] ({project_id})\n"
        f"  Stories: {story_count}, Tasks: {task_count}, Steps: {step_count}"
    )
    if not confirm("Proceed with deletion?", force):
        raise typer.Abort()
    repo.delete_project(engine, project_id)
    console.print(f"[green]Deleted project {project_id}[/green]")


@app.command("ingest")
def ingest(
    path: Annotated[Path, typer.Argument()],
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    raw = json.loads(path.read_text())
    data = ProjectIngest.model_validate(raw)
    story_count = len(data.stories)
    task_count = (
        sum(len(s.tasks) for s in data.stories) + len(data.bugs) + len(data.hotfixes)
    )
    step_count = (
        sum(len(t.steps) for s in data.stories for t in s.tasks)
        + sum(len(t.steps) for t in data.bugs)
        + sum(len(t.steps) for t in data.hotfixes)
    )
    console.print(
        f"Will ingest project [bold]{data.title}[/bold]\n"
        f"  Stories: {story_count}, Tasks: {task_count}, Steps: {step_count}"
    )
    if not confirm("Proceed?", force):
        raise typer.Abort()
    engine = get_engine()
    project = repo.ingest_project(engine, data)
    console.print(
        Panel(
            f"[bold]{project.title}[/bold]\n\nID: {project.id}",
            title="Project ingested",
        )
    )
