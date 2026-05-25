import json
from pathlib import Path

import typer

from db.models import DoDItem


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


def resolve_definition_of_done(
    definition_of_done_file: str | None,
) -> list[DoDItem] | None:
    """Resolve definition-of-done items from a JSON file.

    Returns None if no file is provided (valid for update commands).
    Raises BadParameter if the file cannot be read or contains invalid JSON.
    """
    if definition_of_done_file is None:
        return None
    try:
        raw = Path(definition_of_done_file).read_text()
    except OSError as e:
        raise typer.BadParameter(f"cannot read definition-of-done file: {e}")
    try:
        parsed = json.loads(raw)
        return [DoDItem(**item) for item in parsed]
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        raise typer.BadParameter(f"definition-of-done file must be a JSON array of objects: {e}")
