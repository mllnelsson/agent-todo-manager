import os

import typer


def resolve(flag_value: str | None, env_var: str, flag_name: str) -> str:
    value = flag_value if flag_value is not None else os.environ.get(env_var)
    if not value:
        raise typer.BadParameter(
            f"{flag_name} not provided and {env_var} is not set in the environment"
        )
    return value
