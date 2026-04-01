# ATM CLI — Commands & Services Plan

## Structure

```
atm-cli/
└── src/
    └── atm_cli/
        ├── main.py
        ├── output.py
        ├── db.py
        ├── commands/
        │   ├── projects.py
        │   ├── stories.py
        │   ├── tasks.py
        │   ├── steps.py
        │   └── completions.py      # list only, no write surface
        └── services/
            ├── exceptions.py
            ├── projects.py
            ├── stories.py
            ├── tasks.py
            └── steps.py            # owns all rollup + completion logging logic
```

---

## Exceptions

**`services/exceptions.py`**

| Exception | When |
|---|---|
| `NotFound` | Any repo call returns `None` |
| `InvalidStatus` | Entity is in wrong state for the action (e.g. completing an already-completed step) |

All commands catch these and route to `output.py` → structured JSON error + exit code.

---

## Output Contract

**`output.py`**

- `print_json(data)` — `model_dump(exclude_none=True)` → stdout
- `print_md(data)` — markdown rendering for `--md` flag
- `print_error(code, context)` — `{"error": code, "context": context}` → stdout
- Exit codes: `0` success, `1` user error (`NotFound`, `InvalidStatus`), `2` system error

---

## Commands & Services

### `projects`

| Command | Options | Service | Repo calls |
|---|---|---|---|
| `get <id>` | — | `get_project(engine, id)` | `get_project` (eagerly loads full tree) |

No `list`. Agent is initialized with project ID via env var.

---

### `stories`

| Command | Options | Service | Repo calls |
|---|---|---|---|
| `list` | `--project <id>` | `list_stories(engine, project_id)` | `list_active_stories` — flat, no children |
| `get <uuid>` | — | `get_story(engine, id)` | `get_story` — always returns full task+step tree |
| `get <seq>` | `--project <id>` | `get_story(engine, project_id, seq)` | `get_story_by_seq` — always returns full task+step tree |
| `create` | `--project --title --description` | `create_story(engine, data)` | `create_story` |
| `update <id>` | `--title --description --status` | `update_story(engine, id, data)` | `update_story` |

No `delete`. Too destructive for agent use.

---

### `tasks`

| Command | Options | Service | Repo calls |
|---|---|---|---|
| `get <uuid>` | — | `get_task(engine, id)` | `get_task` — always returns full step tree |
| `get <seq>` | `--story <id>` or `--project <id>` (floating) | `get_task(engine, ...)` | `get_task_by_seq` or `get_floating_task_by_seq` — always returns full step tree |
| `get <seq>` | `--md` | same, rendered as markdown | same |
| `list-floating` | `--project <id>` | `list_floating_tasks(engine, project_id)` | `list_floating_tasks` — flat, no steps |
| `create` | `--story <id> --title --description` | `create_task(engine, data)` | `create_task` |
| `create` | `--project <id> --prefix b --title --description` | same (floating) | `create_task` |
| `update <id>` | `--title --description --status --prefix` | `update_task(engine, id, data)` | `update_task` |

Note: `get` always returns the full step tree regardless of how the task is addressed. `list` commands are always flat.

---

### `steps`

| Command | Options | Service | Repo calls |
|---|---|---|---|
| `get <seq>` | `--task <id>` | `get_step(engine, task_id, seq)` | `get_step_by_seq` |
| `next` | `--task <id>` | `get_next_step(engine, task_id)` | `get_next_step` |
| `create` | `--task <id> --title --description` | `create_step(engine, data)` | `create_step` |
| `update <id>` | `--title --description` | `update_step(engine, id, data)` | `update_step` |
| `start <id>` | `--agent --session [--branch]` | `start_step(engine, ...)` | `update_step` + `create_completion` |
| `complete <id>` | `--agent --session [--branch]` | `complete_step(engine, ...)` | see below |

**`services/steps.py::complete_step()`** — all in one transaction:
1. `update_step` → status `COMPLETED`
2. `create_completion` → action `completed`, entity_type `step`
3. Check all sibling steps — if all `COMPLETED` and at least one exists:
   - `update_task` → status `COMPLETED`
   - `create_completion` → action `completed`, entity_type `task`
4. Check all sibling tasks — if all `COMPLETED` and at least one exists:
   - `update_story` → status `COMPLETED`
   - `create_completion` → action `completed`, entity_type `story`

**`services/steps.py::start_step()`** — in one transaction:
1. `update_step` → status `IN_PROGRESS`
2. `create_completion` → action `started`, entity_type `step`

---

### `completions`

No CLI write surface. All writes happen as side effects of `steps start` and `steps complete`.

| Command | Options | Repo calls |
|---|---|---|
| `list` | `--entity <id>` | `list_completions_by_entity` |
| `active` | — | `list_active_assignments` |

`active` shows all entities currently in flight (latest completion is `started`). Useful for the planning agent to see what the worker is doing.

---

## Worker Agent Command Surface

The minimal set a coding worker needs:

```bash
atm tasks get <seq> --story <id> --md > task.md              # briefing (always includes steps)
atm steps next --task <id>                                       # what to do next
atm steps start <id> --agent <name> --session <id>              # pick up a step
atm steps complete <id> --agent <name> --session <id>           # done, triggers rollup
```

---

## Planning Agent Command Surface

```bash
atm projects get <id>                                            # orient
atm stories list --project <id>                                  # see active stories
atm stories create --project <id> --title ... --description ...  # plan
atm tasks create --story <id> --title ... --description ...      # plan
atm steps create --task <id> --title ... --description ...       # plan
atm completions active                                           # see what's in flight
```
