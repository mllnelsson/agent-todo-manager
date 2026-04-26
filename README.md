# Agent Todo Manager

![Project Dashboard](resources/images/atm.png)
## Overview

A state management system with a structured database at its core, exposed via a Python CLI for agent interaction, a thin FastAPI backend for the GUI, and a Vite frontend for state visibility.

## Architecture

| Module | Role |
|--------|------|
| `db`      | Schema, migrations, and source of truth for all project state |
| `atm-cli` | Agent-facing interface, reads and mutates state directly via the DB |
| `api`     | Thin FastAPI layer, serves state to the GUI |
| `gui`     | Vite dashboard, renders live state via the API |

## Modules

### `db`
The source of truth. All state lives here. The other three modules are downstream of it.

See the db [schema](./db/quick_reference.md) for the information model.

### `cli`
Built for agent consumption, not humans. Hits the DB directly.

- **Output:** Always JSON to stdout. No envelope wrapping. Nulls and empty fields stripped.
- **Errors:** Structured JSON to stdout: `{"error": "code", "context": "..."}`. Diagnostics and logs to stderr only.
- **No interactive prompts. Ever.**
- **Exit codes:** `0` success, `1` user error, `2` system error.
- **Stack:** Python + [Typer](https://typer.tiangolo.com/) + Pydantic (`model_dump(exclude_none=True)`)

### `api`
Thin [FastAPI](https://fastapi.tiangolo.com/) service. Bridges the DB and the GUI. Not a general-purpose API.

### `gui`
[Vite](https://vitejs.dev/) dashboard for observing live state. Two views:

- **Projects** — sidebar lists all projects; selecting one shows stories, tasks, steps, bugs, hotfixes, and activity feed
- **Agents** — shows all in-progress tasks across all projects, grouped by the agent working on each

No business logic. Read-only.

## Getting Started

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 18+

> `atm` is a globally installed tool (`uv tool install`). Other workspace commands (alembic, uvicorn) run via `uv run` from inside the repo.

### 1. Install the `atm` CLI

Easy path — clone, install, migrate, and configure the DB in one step:

```sh
bash <(curl -fsSL https://raw.githubusercontent.com/mllnelsson/agent-todo-manager/main/install.sh)
```

Or manually:

```sh
git clone git@github.com:mllnelsson/agent-todo-manager.git ~/.local/share/atm
uv tool install ~/.local/share/atm/atm-cli
```

The install script:
- Clones the repo to `~/.local/share/atm`
- Installs `atm` globally via `uv tool install`
- Runs DB migrations against `~/.local/share/atm/app.db`
- Adds `ATM_DATABASE_URL` to your shell rc (`~/.zshrc` or `~/.bashrc`)

After running, reload your shell and verify: `atm --help`

### 2. Install GUI dependencies *(optional — only needed for the dashboard)*

```sh
cd ~/.local/share/atm
uv sync       # Python (db + api)
cd gui && npm install
```

### 3. Start the API *(optional)*

```sh
cd ~/.local/share/atm/api
uv run uvicorn main:app --reload
# → http://localhost:8000
```

### 4. Start the GUI *(optional)*

```sh
cd ~/.local/share/atm/gui
npm run dev
# → http://localhost:5173
```

### 5. Create a project

From the root of the consumer project (the repo you want ATM to manage):

```sh
atm admin projects create --title "My Project"
```

This prints the project UUID and prompts to write it to `.atm_project_id` in the current directory. Accept the prompt — the SessionStart hook reads that file to populate `ATM_PROJECT_ID` on every Claude Code session.

For scripted setup, skip the prompt with `--id-file PATH` (add `--force` to overwrite an existing file):

```sh
atm admin projects create --title "My Project" --id-file ./.atm_project_id
```

To list existing projects:

```sh
atm admin projects list
```

### 6. Install agent skills

Copy the ATM skill directory into the target project's Claude Code skills folder:

```sh
cp -r ~/.local/share/atm/resources/skills/atm /path/to/your/project/.claude/skills/atm
```

This installs three skills:

| Skill file | Slash command | Role |
|---|---|---|
| `.claude/skills/atm/SKILL.md` | `/atm` | Common foundation — load this first |
| `.claude/skills/atm/pm-agent/SKILL.md` | `/atm:pm-agent` | PM agent — plans stories, tasks, steps |
| `.claude/skills/atm/dev-agent/SKILL.md` | `/atm:dev-agent` | Dev agent — executes steps |

### 7. Configure agent environment

The CLI reads these three variables from the environment instead of requiring them on every command:

| Variable | Value | Description |
|---|---|---|
| `ATM_PROJECT_ID` | UUID from step 5 | Default project for commands that accept `--project`. Set automatically from `<repo-root>/.atm_project_id` |
| `ATM_SESSION_ID` | A unique UUID per session | Ties completions to a specific agent run |
| `ATM_AGENT_NAME` | Agent identity (e.g. `Claude`, `plan`, `build`) | Recorded as the `agent` on `tasks start` / `tasks complete` / `steps start` / `steps complete` |

When running inside Claude Code the SessionStart hook (`resources/plugin/hooks/atm_session_start.sh`) sets all three automatically — `ATM_PROJECT_ID` is read from `<repo-root>/.atm_project_id` (created in step 5) and the other two from the session payload. You can ignore this step in that case.

When invoking the CLI from a plain shell, export them yourself:

```sh
export ATM_PROJECT_ID=<uuid from step 5>
export ATM_SESSION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")
export ATM_AGENT_NAME=manual
```

The corresponding `--project`, `--session`, and `--agent` flags remain available as explicit overrides.

## What We're NOT Optimizing For

- Pretty CLI output
- Shell completion
- Rich formatting (`TYPER_USE_RICH=0` in agent context)
