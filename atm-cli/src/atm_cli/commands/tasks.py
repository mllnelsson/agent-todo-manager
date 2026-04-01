import typer

from db.models import Status, TaskCreate, TaskUpdate

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json, print_list, print_md
from ..services.exceptions import NotFound
from ..services.tasks import (
    create_task_for_story,
    get_floating_task_by_project_seq,
    get_task_by_id,
    get_task_by_story_seq,
    list_floating_tasks_for_project,
    update_task_by_id,
)

app = typer.Typer(no_args_is_help=True)


def _is_uuid(value: str) -> bool:
    import uuid
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def _render_task_md(task) -> str:
    status_map = {
        Status.TODO: "TODO",
        Status.IN_PROGRESS: "IN_PROGRESS",
        Status.COMPLETED: "COMPLETED",
    }
    lines = [f"# [{task.seq}] {task.title}", "", task.description]
    if task.steps:
        lines += ["", "## Steps"]
        for step in task.steps:
            lines.append(f"{step.seq}. [{status_map.get(step.status, step.status)}] {step.title}")
    return "\n".join(lines)


@app.command("get")
def get(
    id_or_seq: str,
    story: str | None = typer.Option(None, "--story", help="Story ID (required for seq lookup)"),
    project: str | None = typer.Option(None, "--project", help="Project ID (for floating task seq lookup)"),
    md: bool = typer.Option(False, "--md", help="Render as markdown"),
) -> None:
    engine = get_engine()
    try:
        if _is_uuid(id_or_seq):
            task = get_task_by_id(id_or_seq, engine)
        elif story:
            task = get_task_by_story_seq(story, int(id_or_seq), engine)
        elif project:
            task = get_floating_task_by_project_seq(project, int(id_or_seq), engine)
        else:
            raise typer.BadParameter("--story or --project is required when using a sequence number")

        if md:
            print_md(_render_task_md(task))
        else:
            print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("list-floating")
def list_floating(project: str = typer.Option(..., "--project", help="Project ID")) -> None:
    engine = get_engine()
    try:
        tasks = list_floating_tasks_for_project(project, engine)
        print_list(tasks)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("create")
def create(
    story: str | None = typer.Option(None, "--story", help="Story ID"),
    project: str | None = typer.Option(None, "--project", help="Project ID (for floating tasks)"),
    prefix: str | None = typer.Option(None, "--prefix", help="Prefix for floating tasks (b=bug, h=hotfix)"),
    title: str = typer.Option(..., "--title"),
    description: str = typer.Option(..., "--description"),
) -> None:
    engine = get_engine()
    try:
        if story is None and project is None:
            raise typer.BadParameter("--story or --project is required")
        data = TaskCreate(
            story_id=story,
            project_id=project or "",
            prefix=prefix,
            title=title,
            description=description,
        )
        task = create_task_for_story(data, engine)
        print_json(task)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("update")
def update(
    id: str,
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
    status: str | None = typer.Option(None, "--status"),
    prefix: str | None = typer.Option(None, "--prefix"),
) -> None:
    engine = get_engine()
    try:
        data = TaskUpdate(
            title=title,
            description=description,
            status=Status(status) if status else None,
            prefix=prefix,
        )
        task = update_task_by_id(id, data, engine)
        print_json(task)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
