# dashboard

FastAPI app that serves the read API and the built GUI from a single origin.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}` | Project detail with activity completions |
| `GET` | `/...` | Static GUI assets from `gui/dist` (SPA fallback) |

## Setup

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node 18+ (to build the GUI)

Install dependencies from the workspace root:

```sh
uv sync
```

Build the GUI once so the app has something to serve:

```sh
cd gui && npm install && npm run build
```

## Configuration

- `ATM_DATABASE_URL` — required. Example: `sqlite:////absolute/path/to/app.db`.
- `ATM_GUI_DIST` — optional. Absolute path to the built GUI directory. If unset, the app looks for `gui/dist` next to the workspace root.

## Running

The bundled command starts the dashboard with one invocation:

```sh
atm admin serve
```

Or run uvicorn directly during development:

```sh
cd dashboard
uv run uvicorn main:app --reload
```

The dashboard starts at `http://localhost:8000`. Interactive API docs are at `http://localhost:8000/docs`.
