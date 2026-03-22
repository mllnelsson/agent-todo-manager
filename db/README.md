# atm

Agent task manager. A structured DB at the core, exposed via a CLI for agent interaction, a thin API for the GUI, and a Vite frontend for state visibility.

## Architecture

| Module    | Role |
|-----------|------|
| `db`      | Schema and migrations. Source of truth. |
| `atm-cli` | Agent-facing CLI. Reads and mutates state directly via the DB. |
| `api`     | Thin FastAPI layer. Bridges DB and GUI. |
| `gui`     | Vite app. Renders current state. Read-only. |

## Data Model

Work is organised as `x.y.z` — story, task, step. Floating tasks (bugs, hotfixes) use a letter prefix instead: `b.2.3`, `h.1.4`.

```
project → stories → tasks → steps
        ↘ floating tasks   ↗
```

All state transitions are logged in `completions`, including agent name, session, and branch. See [`db/schema.md`](db/schema.md) for the full information model.

## CLI Contract

- Output: always JSON to stdout, no envelope wrapping, nulls stripped
- Errors: `{"error": "code", "context": "..."}` to stdout
- Logs and diagnostics: stderr only
- No interactive prompts. Ever.
- Exit codes: `0` success, `1` user error, `2` system error
- Stack: Python + Typer + Pydantic (`model_dump(exclude_none=True)`)

## Not Optimising For

Pretty output, shell completion, Rich formatting. Set `TYPER_USE_RICH=0` in agent context.
