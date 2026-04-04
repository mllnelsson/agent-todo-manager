import typer

from .commands import projects, prune, steps, stories, tasks

app = typer.Typer(name="atm-admin", no_args_is_help=True)
app.add_typer(projects.app, name="projects")
app.add_typer(stories.app, name="stories")
app.add_typer(tasks.app, name="tasks")
app.add_typer(steps.app, name="steps")
app.add_typer(prune.app, name="prune")


def main() -> None:
    app()
