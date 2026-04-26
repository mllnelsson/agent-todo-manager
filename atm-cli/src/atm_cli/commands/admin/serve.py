import os
from pathlib import Path
from typing import Annotated

import typer


def serve(
    host: Annotated[str, typer.Option("--host")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port")] = 8000,
    gui_dist: Annotated[
        Path | None,
        typer.Option("--gui-dist", help="Path to built gui/dist directory"),
    ] = None,
) -> None:
    """Run the bundled dashboard (GUI + read API) on a single port."""
    if gui_dist is not None:
        os.environ["ATM_GUI_DIST"] = str(gui_dist.resolve())

    import uvicorn

    from dashboard.main import app

    uvicorn.run(app, host=host, port=port)
