# atm-admin — Admin CLI Plan

## Overview

A new human-facing CLI (`atm-admin`) for administrative operations: creating projects,
ingesting structured JSON, deleting entities with full cascade, and pruning dirty/stale state.

Sits alongside `atm-cli` (agent-facing, JSON-only) as a separate workspace member.
Reuses the `db` package for all data access.

---

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Separate CLI vs flags on `atm` | Separate | `atm` is agent-facing (JSON, no prompts). Admin needs rich output + confirmations. |
| Output | `rich` tables + styled text | Human-readable. No JSON mode needed. |
| Cascade deletes | Application-layer | No FK CASCADE in DB. Explicit delete order: completions -> steps -> tasks -> stories -> project. More transparent for admin. |
| Completions cleanup | Delete alongside entity | `completions.entity_id` has no FK — must be cleaned explicitly. Collect all entity IDs in subtree, bulk-delete matching completions. |
| New DB migration | No | No schema changes. All new functionality uses existing tables and columns. |
| Confirmation prompts | Yes, with `--force` to skip | Destructive operations show what will be deleted and ask for confirmation. |

---

## Scope

### In scope
- Fix existing broken `delete_story`, `delete_task`, `delete_step` repo functions (FK cascade)
- Project CRUD (create, list, delete)
- JSON ingest (create a full project tree from a single JSON file)
- Cascading hard delete for any entity (project, story, task, step)
- Prune commands (stale items, dirty state detection and cleanup)
- Human-friendly output via `rich`

### Out of scope
- New DB statuses (e.g. `ARCHIVED`)
- New migrations
- API endpoints for admin
- GUI changes

---

## db layer changes

Changes to `db/src/db/repo/`. These are reusable by any consumer
(admin CLI, existing atm CLI, future API endpoints, etc).

### Bug fix: existing delete functions

**Problem:** `delete_story` and `delete_task` will raise FK constraint errors
when the entity has children, because no CASCADE is configured at the DB or ORM level.
`delete_step` works (leaf node) but leaves orphaned completion records.

**Fix:** Rewrite all three existing delete functions to properly cascade. This is a
correctness fix — not new behaviour. The functions already promise to delete; they
just fail when children exist. The `atm` CLI does not expose delete commands, so
there are no callers to break.

**`db/src/db/repo/step.py` — fix `delete_step`:**
```
delete_step(engine, step_id: str) -> bool
    1. Delete completions where entity_id = step_id
    2. Delete the step row
    Returns False if step not found.
```

**`db/src/db/repo/task.py` — fix `delete_task`:**
```
delete_task(engine, task_id: str) -> bool
    1. Collect entity IDs: task_id + all child step IDs
    2. Delete completions where entity_id IN collected IDs
    3. Delete all child steps
    4. Delete the task row
    Returns False if task not found.
```

**`db/src/db/repo/story.py` — fix `delete_story`:**
```
delete_story(engine, story_id: str) -> bool
    1. Collect entity IDs: story_id + all child task IDs + all grandchild step IDs
    2. Delete completions where entity_id IN collected IDs
    3. Delete all grandchild steps
    4. Delete all child tasks
    5. Delete the story row
    Returns False if story not found.
```

All three must execute within a single session/transaction so partial deletes
cannot leave the DB in an inconsistent state.

### New functions

#### `db/src/db/repo/project.py`

```
create_project(engine, data: ProjectCreate) -> Project
    Create a new project. Assigns UUID, sets status=TODO.

delete_project(engine, project_id: str) -> bool
    Delete project and ALL children: stories, tasks (story + floating), steps.
    Also deletes all completions referencing any entity in the subtree.
    Returns False if project not found.
    Delete order (single transaction): completions -> steps -> tasks -> stories -> project.
```

#### `db/src/db/repo/completion.py`

```
delete_completions_by_entity_ids(engine, entity_ids: list[str]) -> int
    Bulk-delete all completion records whose entity_id is in the given list.
    Returns count of deleted rows.
    Used internally by the cascade delete functions above, but also exported
    for direct use by admin CLI prune commands.
```

#### Query functions for pruning — `db/src/db/repo/queries.py` (new file)

```
list_stale_tasks(engine, project_id: str, days: int) -> list[Task]
    Tasks whose updated_at is older than `days` ago and status != COMPLETED.

list_stale_steps(engine, project_id: str, days: int) -> list[Step]
    Steps whose updated_at is older than `days` ago and status == IN_PROGRESS.
    These are "stuck" steps — started but never finished.

list_orphaned_tasks(engine, project_id: str) -> list[Task]
    Tasks with status != COMPLETED whose parent story has status == COMPLETED.
    This is inconsistent state — the story was marked done but children weren't.

list_todo_in_completed_stories(engine, project_id: str) -> list[Task]
    Tasks with status == TODO in stories that are COMPLETED.
    Work that was planned but never started in a finished story.
```

---

## atm-admin package structure

```
atm-admin/
  pyproject.toml
  src/
    atm_admin/
      __init__.py          # exports main
      main.py              # Typer app, command group registration
      config.py            # BaseSettings (same pattern as atm-cli)
      db.py                # Engine singleton (same pattern as atm-cli)
      output.py            # rich table/panel helpers
      errors.py            # AdminError, NotFoundError
      commands/
        __init__.py
        projects.py        # create, list, delete, ingest
        stories.py         # delete (cascading)
        tasks.py           # delete (cascading)
        steps.py           # delete
        prune.py           # stale, dirty-state, cleanup
```

### pyproject.toml

```toml
[project]
name = "atm-admin"
version = "0.1.0"
description = "Admin CLI for ATM — human-facing project management and pruning"
requires-python = ">=3.12"
dependencies = [
    "typer>=0.24.1",
    "rich>=14.0.0",
    "pydantic>=2.12.5",
    "pydantic-settings>=2.13.1",
    "db",
]

[tool.uv.sources]
db = { workspace = true }

[project.scripts]
atm-admin = "atm_admin:main"

[build-system]
requires = ["uv_build>=0.10.9,<0.11.0"]
build-backend = "uv_build"
```

### Workspace registration

Add `"atm-admin"` to the `members` list in root `pyproject.toml`:

```toml
[tool.uv.workspace]
members = ["db", "atm-cli", "api", "atm-admin"]
```

---

## Commands

### `atm-admin projects create`

```
atm-admin projects create --title "My Project" --description "Description"
```

Creates a top-level project. Prints a rich panel with the created project details.

### `atm-admin projects list`

```
atm-admin projects list [--all]
```

Lists projects as a rich table. By default shows active (non-COMPLETED) only.
`--all` includes completed.

### `atm-admin projects delete`

```
atm-admin projects delete PROJECT_ID [--force]
```

Shows the full project tree that will be deleted (stories, tasks, steps count + completion count).
Asks for confirmation unless `--force`. Cascade-deletes everything.

### `atm-admin projects ingest`

```
atm-admin projects ingest PATH_TO_JSON [--force]
```

Reads a JSON file and creates a full project tree in a single transaction.

**JSON schema:**

```json
{
  "title": "Project title",
  "description": "Project description",
  "stories": [
    {
      "title": "Story 1",
      "description": "...",
      "tasks": [
        {
          "title": "Task 1",
          "description": "...",
          "steps": [
            { "title": "Step 1", "description": "..." }
          ]
        }
      ]
    }
  ],
  "bugs": [
    {
      "title": "Bug 1",
      "description": "...",
      "steps": [...]
    }
  ],
  "hotfixes": [
    {
      "title": "Hotfix 1",
      "description": "...",
      "steps": [...]
    }
  ]
}
```

Shows a summary of what will be created (X stories, Y tasks, Z steps) and confirms.
Creates everything in one DB transaction. On failure, rolls back entirely.

**Pydantic models for ingest** — defined in `db/src/db/models/ingest.py`:

```
StepIngest(BaseModel):   title, description
TaskIngest(BaseModel):   title, description, steps: list[StepIngest]
StoryIngest(BaseModel):  title, description, tasks: list[TaskIngest]
ProjectIngest(BaseModel): title, description, stories: list[StoryIngest],
                           bugs: list[TaskIngest], hotfixes: list[TaskIngest]
```

**Repo function** — `db/src/db/repo/project.py`:

```
ingest_project(engine, data: ProjectIngest) -> Project
    Single transaction. Creates project, stories (with seq), tasks (with seq),
    steps (with seq). Returns the fully populated Project model.
```

### `atm-admin stories delete`

```
atm-admin stories delete STORY_ID [--force]
```

Calls `db.repo.delete_story` (now fixed to cascade). Shows what will be deleted first.

### `atm-admin tasks delete`

```
atm-admin tasks delete TASK_ID [--force]
```

Calls `db.repo.delete_task` (now fixed to cascade). Shows what will be deleted first.

### `atm-admin steps delete`

```
atm-admin steps delete STEP_ID [--force]
```

Calls `db.repo.delete_step` (now fixed to clean completions). Shows what will be deleted first.

### `atm-admin prune stale`

```
atm-admin prune stale --project PROJECT_ID --days 7 [--force]
```

Finds tasks/steps not updated in N days that are not COMPLETED.
Shows a table of stale items. With confirmation, deletes them (cascade).

### `atm-admin prune stuck`

```
atm-admin prune stuck --project PROJECT_ID [--force]
```

Finds steps that are IN_PROGRESS but have no recent completion activity.
These are likely abandoned work. Shows them, offers to reset to TODO or delete.

### `atm-admin prune dirty`

```
atm-admin prune dirty --project PROJECT_ID [--force]
```

Finds inconsistent state:
- Tasks status != COMPLETED in stories that are COMPLETED
- Tasks with status TODO in stories marked COMPLETED (never started, planned but abandoned)
- Steps in COMPLETED tasks that aren't COMPLETED themselves

Shows a report. With confirmation, deletes the dirty entities (cascade) and their completions.

---

## Implementation order

The implementing agent should follow this sequence:

### Phase 1: Fix existing broken deletes
1. Add `delete_completions_by_entity_ids` to `db/src/db/repo/completion.py`
2. Fix `delete_step` in `db/src/db/repo/step.py` — delete related completions before the step
3. Fix `delete_task` in `db/src/db/repo/task.py` — cascade: completions -> steps -> task
4. Fix `delete_story` in `db/src/db/repo/story.py` — cascade: completions -> steps -> tasks -> story

### Phase 2: New DB layer functions
1. Add `create_project` to `db/src/db/repo/project.py`
2. Add `delete_project` (cascading) to `db/src/db/repo/project.py`
3. Create `db/src/db/repo/queries.py` with stale/dirty query functions
4. Create `db/src/db/models/ingest.py` with ingest Pydantic models
5. Add `ingest_project` to `db/src/db/repo/project.py`
6. Update `db/src/db/repo/__init__.py` and `db/src/db/models/__init__.py` exports
7. Update `db/REPO_REFERENCE.md` with new functions

### Phase 3: atm-admin package scaffold
1. Create `atm-admin/` directory structure
2. Create `pyproject.toml`
3. Add `"atm-admin"` to workspace members in root `pyproject.toml`
4. Create `config.py`, `db.py` (same pattern as atm-cli)
5. Create `output.py` with rich helpers (table printer, confirmation prompt, tree display)
6. Create `errors.py`
7. Create `main.py` with Typer app
8. Create `__init__.py` exporting `main`

### Phase 4: Commands
1. `commands/projects.py` — create, list, delete, ingest
2. `commands/stories.py` — delete
3. `commands/tasks.py` — delete
4. `commands/steps.py` — delete
5. `commands/prune.py` — stale, stuck, dirty

### Phase 5: Validation
1. `uv sync` from root — confirm atm-admin installs
2. `uv run atm-admin --help` — confirm all commands register
3. `uv run ruff check atm-admin/` — lint clean
4. `uv run ruff format atm-admin/` — formatted
5. Manual smoke test of create + ingest + delete + prune

---

## Guidelines for the implementing agent

- Follow `/coding-guidelines` and `/coding-guidelines/python/SKILL.md`
- Use `uv run`, never bare `python`
- Use return type annotations on all functions
- Use `StrEnum` + `match/case` for any new enums
- Functions, not classes — imperative style
- `rich` for all human output: `Table`, `Panel`, `Confirm.ask()`, `console.print()`
- All destructive commands must confirm before acting (unless `--force`)
- Error handling at CLI boundary only — services raise, commands catch and display
- No docstrings/comments beyond what's necessary for non-obvious logic
- Run `ruff check` and `ruff format` before committing
