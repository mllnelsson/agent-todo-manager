---
name: python-guidelines
description: Python-specific coding guidelines. Use when writing or reviewing Python code. Apply on top of the general coding-guidelines skill.
---

Use this skill when writing or reviewing Python code. These are guiding principles — code breaking these standards is generally not accepted.

## General code style

Write in an imperative / C-like manner: prefer functions that manipulate data classes over stateful classes with methods. Avoid classes unless using abstractions or 3rd party integrations.

```python
# preferred
def calculate_total(order: Order) -> float:
    return sum(item.price for item in order.items)

# avoid (unless abstraction warrants it)
class OrderService:
    def calculate_total(self, order): ...
```

## OOP

Avoid OOP and introducing those patterns as much as possible. AI assistants have a strong tendency to reach for classes in Python — resist this. A module with functions is almost always the right answer.

## Config

Use pydantic `BaseSettings` loaded from a `.env` file. Multiple `BaseSettings` classes are fine; avoid multiple `.env` files.

```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    database_url: str
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")

config = AppConfig()
```

## Data classes

Use pydantic `BaseModel` for data objects. Keep them logic-free — put mapping, construction, and transformation in separate functions.

```python
class User(BaseModel):
    id: int
    name: str
    email: str

def user_from_row(row: dict) -> User:
    return User(**row)
```

## Type hints

Use modern type hint syntax.

```python
# good
def find(id: int) -> User | None: ...
def merge(a: str | bytes) -> str: ...

# avoid
from typing import Optional, Union
def find(id: int) -> Optional[User]: ...
```

## Modules

Group shared logic into modules. Use `__init__.py` to define the public API — only export what callers should use.

```
users/
  __init__.py      # exports: get_user, create_user
  _queries.py      # internal DB queries
  _models.py       # internal models
```

## Private methods

Prefix with `_` any function used only within a single file.

```python
def _parse_raw(data: bytes) -> dict: ...  # internal
def load_config(path: str) -> Config: ... # public
```

## Error handling

Define custom exception classes rather than raising generic exceptions. Group them in an `errors.py` module within the relevant package.

```python
# errors.py
class AppError(Exception): ...
class UserNotFoundError(AppError): ...
class InvalidCredentialsError(AppError): ...

# usage
def get_user(id: int) -> User:
    user = db.find(id)
    if not user:
        raise UserNotFoundError(f"User {id} not found")
    return user
```

## Constants

Always use `UPPER_CASE` for module-level constants.

```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0
```

## Enums and match

Use `StrEnum` to model finite sets of options. Use `match`/`case` for exhaustive handling — never `if/elif` chains.

```python
from enum import StrEnum, auto

class Status(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    PENDING = auto()

def describe(status: Status) -> str:
    match status:
        case Status.ACTIVE:
            return "User is active"
        case Status.INACTIVE:
            return "User is inactive"
        case Status.PENDING:
            return "Awaiting activation"
```

`StrEnum` values compare equal to their string equivalents, making them safe to use with JSON payloads and databases without manual conversion.
