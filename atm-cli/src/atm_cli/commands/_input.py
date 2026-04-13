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


def resolve_definition_of_done(
    definition_of_done: str | None, definition_of_done_file: str | None
) -> str | None:
    """Resolve definition-of-done text from --definition-of-done or --definition-of-done-file.

    Returns None if neither is provided (valid for update commands).
    Raises BadParameter if both are provided or the file cannot be read.
    """
    if definition_of_done is not None and definition_of_done_file is not None:
        raise typer.BadParameter(
            "--definition-of-done and --definition-of-done-file are mutually exclusive"
        )
    if definition_of_done_file is not None:
        try:
            return Path(definition_of_done_file).read_text()
        except OSError as e:
            raise typer.BadParameter(f"cannot read definition-of-done file: {e}")
    return definition_of_done
