from rich.console import Console
from rich.table import Table

console = Console()


def confirm(message: str, force: bool) -> bool:
    if force:
        return True
    from rich.prompt import Confirm

    return Confirm.ask(message)


def print_table(title: str, columns: list[str], rows: list[list[str]]) -> None:
    table = Table(title=title, show_lines=True)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)
