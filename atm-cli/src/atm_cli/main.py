import typer

from .commands import completions, projects, steps, stories, tasks

app = typer.Typer(name="atm", no_args_is_help=True)
app.add_typer(projects.app, name="projects")
app.add_typer(stories.app, name="stories")
app.add_typer(tasks.app, name="tasks")
app.add_typer(steps.app, name="steps")
app.add_typer(completions.app, name="completions")


def main() -> None:
    app()
