# Project Name

## Overview

A state management system with a structured database at its core, exposed via a Python CLI for agent interaction, a thin FastAPI backend for the GUI, and a Vite frontend for state visibility.

## Architecture

| Module | Role |
|--------|------|
| `db`  | Schema, migrations, and source of truth for all project state |
| `cli` | Agent-facing interface, reads and mutates state directly via the DB |
| `api` | Thin FastAPI layer, serves state to the GUI |
| `gui` | Lightweight Vite app, renders current state via the API |

## Modules

### `db`
The source of truth. All state lives here. The other three modules are downstream of it.

### `cli`
Built for agent consumption, not humans. Hits the DB directly.

- **Output:** Always JSON to stdout. No envelope wrapping. Nulls and empty fields stripped.
- **Errors:** Structured JSON to stdout: `{"error": "code", "context": "..."}`. Diagnostics and logs to stderr only.
- **No interactive prompts. Ever.**
- **Exit codes:** `0` success, `1` user error, `2` system error.
- **Stack:** Python + [Typer](https://typer.tiangolo.com/) + Pydantic (`model_dump(exclude_none=True)`)

### `api`
Thin [FastAPI](https://fastapi.tiangolo.com/) service. Exists solely to bridge the DB and the GUI. Not a general-purpose API.

### `gui`
[Vite](https://vitejs.dev/) app for observing current state. No business logic. Read-oriented.

## What We're NOT Optimizing For

- Pretty CLI output
- Shell completion
- Rich formatting (`TYPER_USE_RICH=0` in agent context)
