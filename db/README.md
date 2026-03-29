# db

Schema, migrations, ORM, and repository layer. The source of truth for all project state.

## Data Model

Work is organised as `x.y.z` — story, task, step. Floating tasks (bugs, hotfixes) use a letter prefix instead: `b.2.3`, `h.1.4`.

```
project → stories → tasks → steps
        ↘ floating tasks   ↗
```

All state transitions are logged in `completions`, including agent name, session, and branch.

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

Install dependencies from the workspace root:

```sh
uv sync
```

## Configuration

The database URL is read from the `ATM_DATABASE_URL` environment variable. Copy the example and set a path:

```sh
cp .env.example .env
# Edit .env and set ATM_DATABASE_URL=sqlite:////absolute/path/to/app.db
```

## Running Migrations

Migrations are managed with Alembic. Run from the `db/` directory:

```sh
cd db
uv run alembic upgrade head
```

This creates the database file (if using SQLite) and applies all schema migrations.

## Tests

```sh
cd db
uv run pytest
```

Tests run against an in-memory SQLite database.
