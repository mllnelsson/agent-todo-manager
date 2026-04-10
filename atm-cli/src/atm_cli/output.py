import json
import sys

from pydantic import BaseModel


def print_json(data: BaseModel) -> None:
    print(json.dumps(data.model_dump(exclude_none=True), default=str))


def print_list(data: list[BaseModel]) -> None:
    print(json.dumps([d.model_dump(exclude_none=True) for d in data], default=str))


def print_error(code: str, context: str) -> None:
    print(json.dumps({"error": code, "context": context}))


def exit_user_error(code: str, context: str) -> None:
    print_error(code, context)
    sys.exit(1)


def exit_system_error(code: str, context: str) -> None:
    print_error(code, context)
    sys.exit(2)
