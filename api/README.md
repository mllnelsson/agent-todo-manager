# api

Thin FastAPI service. Bridges the database and the GUI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}` | Project detail with activity completions |

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

Install dependencies from the workspace root:

```sh
uv sync
```

## Configuration

Requires `ATM_DATABASE_URL` to be set in your shell config (`~/.bashrc` or `~/.zshrc`):

```sh
export ATM_DATABASE_URL=sqlite:////absolute/path/to/app.db
```

Make sure the database has been migrated before starting the API (see `db/README.md`).

## Running

```sh
cd api
uv run uvicorn main:app --reload
```

The API starts at `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.
