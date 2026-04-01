import typer

from db.repo import list_active_assignments, list_completions_by_entity

from ..db import get_engine
from ..output import exit_system_error, print_list

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_cmd(entity: str = typer.Option(..., "--entity", help="Entity ID")) -> None:
    engine = get_engine()
    try:
        completions = list_completions_by_entity(engine, entity_id=entity)
        print_list(completions)
    except Exception as e:
        exit_system_error("internal_error", str(e))


@app.command("active")
def active() -> None:
    engine = get_engine()
    try:
        completions = list_active_assignments(engine)
        print_list(completions)
    except Exception as e:
        exit_system_error("internal_error", str(e))
