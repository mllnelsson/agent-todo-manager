import typer

from .commands import completions, projects, steps, stories, tasks
from .commands.admin import app as admin_app

app = typer.Typer(name="atm", no_args_is_help=True)
app.add_typer(projects.app, name="projects")
app.add_typer(stories.app, name="stories")
app.add_typer(tasks.app, name="tasks")
app.add_typer(steps.app, name="steps")
app.add_typer(completions.app, name="completions")
app.add_typer(admin_app, name="admin")


def main() -> None:
    app()
