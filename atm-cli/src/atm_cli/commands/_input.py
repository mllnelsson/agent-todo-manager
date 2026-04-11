from pathlib import Path

import typer


def resolve_description(
    description: str | None, description_file: str | None
) -> str | None:
    """Resolve description text from --description or --description-file.

    Returns None if neither is provided (valid for update commands).
    Raises BadParameter if both are provided or the file cannot be read.
    """
    if description is not None and description_file is not None:
        raise typer.BadParameter(
            "--description and --description-file are mutually exclusive"
        )
    if description_file is not None:
        try:
            return Path(description_file).read_text()
        except OSError as e:
            raise typer.BadParameter(f"cannot read description file: {e}")
    return description
