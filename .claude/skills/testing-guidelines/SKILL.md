---
description: This skills outlines the testing philosophy. Use this skill before writing any tests.
---

# Philosophy
Only write tests for business logic. For those methods and lines, strive for 100% coverage. Tests act as a contract for future updates.

## Integration vs Unit
Always create unit tests for modules. Unit tests must be well isolated and mock the behaviour of every dependency from the targeted module.

IMPORTANT: Do not write integration tests unless explicitly told to. Integration tests should aim to cover a feature of an entire app and test end-to-end for that feature.

## Framework
Depending on the tech stack use:
- `pytest` for Python projects (invoke with `uv run pytest`)
- `vitest` for Vite projects

See the respective skill (if available) for each framework.

## Naming conventions
Test files mirror the module they test: `test_<module_name>.py`. Test functions follow `test_<function_name>_<scenario>`.

```
users/
  _queries.py
tests/
  test_queries.py   # tests for users/_queries.py
```

```python
def test_get_user_returns_user_when_found(): ...
def test_get_user_raises_when_not_found(): ...
```

## Fixtures
Use pytest fixtures to share setup across tests. Define them in `conftest.py` at the relevant directory level.

```python
# conftest.py
@pytest.fixture
def user():
    return User(id=1, name="Alice", email="alice@example.com")

# test_queries.py
def test_get_user_returns_user_when_found(user):
    ...
```

## What NOT to test
- Simple data classes that are only initialized do not require tests.
- 3rd party framework tests are handled by those frameworks.

