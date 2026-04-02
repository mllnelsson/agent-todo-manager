import typer

from ..db import get_engine
from ..output import exit_system_error, exit_user_error, print_json
from ..services.exceptions import NotFound
from ..services.project import get_project_by_id

app = typer.Typer(no_args_is_help=True)


@app.command("get")
def get(id: str) -> None:
    """Fetch a project by ID and print it as JSON.

    Args:
        id: UUID of the project.
    """
    engine = get_engine()
    try:
        project = get_project_by_id(id, engine)
        print_json(project)
    except NotFound as e:
        exit_user_error("not_found", str(e))
    except Exception as e:
        exit_system_error("internal_error", str(e))
