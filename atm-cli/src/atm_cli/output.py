import json
import sys

from pydantic import BaseModel


def print_json(data: BaseModel) -> None:
    """Serialise a Pydantic model to JSON and print it to stdout, omitting None fields.

    Args:
        data: Pydantic model instance to serialise.
    """
    print(json.dumps(data.model_dump(exclude_none=True), default=str))


def print_list(data: list[BaseModel]) -> None:
    """Serialise a list of Pydantic models to a JSON array and print it to stdout.

    Args:
        data: List of Pydantic model instances to serialise.
    """
    print(json.dumps([d.model_dump(exclude_none=True) for d in data], default=str))


def print_error(code: str, context: str) -> None:
    """Print a JSON-encoded error object to stdout.

    Args:
        code: Machine-readable error code.
        context: Human-readable error detail.
    """
    print(json.dumps({"error": code, "context": context}))


def exit_user_error(code: str, context: str) -> None:
    """Print a JSON error and exit with code 1 (user/input error).

    Args:
        code: Machine-readable error code.
        context: Human-readable error detail.
    """
    print_error(code, context)
    sys.exit(1)


def exit_system_error(code: str, context: str) -> None:
    """Print a JSON error and exit with code 2 (unexpected system error).

    Args:
        code: Machine-readable error code.
        context: Human-readable error detail.
    """
    print_error(code, context)
    sys.exit(2)
