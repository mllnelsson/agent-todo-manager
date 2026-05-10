import subprocess
from pathlib import Path
from typing import Annotated

import typer

from .output import confirm, console

DEFAULT_INSTALL_DIR = Path.home() / ".local" / "share" / "atm"


def self_update(
    install_dir: Annotated[Path, typer.Option("--install-dir")] = DEFAULT_INSTALL_DIR,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
) -> None:
    """Update atm to the latest version by re-running install.sh."""
    script = install_dir / "install.sh"
    if not script.exists():
        console.print(f"[red]install.sh not found at {script}[/red]")
        raise typer.Exit(1)
    console.print(
        f"Will re-run [bold]{script}[/bold] "
        "(git pull + reinstall + GUI build + migrations)"
    )
    if not confirm("Proceed?", force):
        raise typer.Abort()
    subprocess.run(["sh", str(script)], check=True, cwd=install_dir)
    console.print("[green]atm updated[/green]")
