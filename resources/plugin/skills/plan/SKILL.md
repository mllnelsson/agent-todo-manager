---
name: plan
description: ATM skill for planning and structuring work — owns hierarchy creation (stories, tasks, steps).
---

# ATM Plan

Load this skill to plan and structure work. It covers creating and organising the project hierarchy that the build role then executes.

Load the common foundation first: `/atm:core`

## Commands

### Retrieval (delegate to `atm-lookup`)

| Command | Purpose |
|---|---|
| `atm stories list [--all]` | List stories (active only by default; `--all` includes completed) |
| `atm stories get <ID_OR_SEQ>` | Fetch a story by UUID or seq (embeds task array) |
| `atm tasks list-floating` | List floating tasks |
| `atm steps get <SEQ> --task <TASK_ID>` | Fetch step details |

See cli-reference.md for full syntax and optional flags on all commands.

### Mutations (run directly)

| Command | Purpose |
|---|---|
| `atm stories create` | Create a new story |
| `atm stories update <ID>` | Update story fields or status |
| `atm tasks create --story <STORY_ID>` | Create a task under a story |
| `atm tasks create --project <PROJECT_ID>` | Create a floating task (bug, hotfix) |
| `atm tasks update <ID>` | Update task fields |
| `atm steps create --task <TASK_ID>` | Define a step within a task |
| `atm steps update <ID>` | Update step title or description |
| `atm tasks delete <ID>` | Delete a task and all its steps (cleanup) |
| `atm steps delete <SEQ> --task <TASK_ID>` | Delete a step within a task (cleanup) |

See cli-reference.md for full syntax and optional flags on all commands.

## Workflow

1. **Load project context** → delegate to `atm-lookup`: "get project `<PROJECT_ID>`"
2. **Review existing stories** → delegate to `atm-lookup`: "list stories"
3. **Create or update stories** → `stories create` / `stories update`
4. **Decompose stories into tasks** → `tasks create --story <STORY_ID> ...`
5. **Define steps for each task** → `steps create --task <TASK_ID> ...` (one step per discrete unit of work)
6. **Monitor progress** → delegate to `atm-lookup`: "show active assignments" / "list completions for `<ENTITY_ID>`"

## Notes

- **`stories list` returns story metadata only — no tasks.** To see a story's tasks, use `atm stories get <ID_OR_SEQ>`; the response embeds the full task array. There is no `tasks list --story` command. Pass `--all` to include completed stories.
- Tasks must have at least one step defined before the build role can pick them up. Always create steps for every task before handoff.
- **Steps have no status.** They are an ordered breakdown — sequencing hints — that tell the build agent how to slice up a task's work. The build agent reads them in order and calls `tasks complete` when finished. Do not attempt to mark steps `in_progress` or `completed`; there is no command for it.
- The step **description** is the implementation specification — it should contain enough detail to complete the step without further questions. Write descriptions as clear, actionable instructions.
- Always use `--description-file` rather than `--description` for descriptions (and `--definition-of-done-file` rather than `--definition-of-done`). Write the content to a tempfile first, then pass the path. This avoids shell escaping issues with long text, newlines, and special characters: `cat > /tmp/desc.md << 'EOF' ... EOF && atm steps create ... --description-file /tmp/desc.md`
- Use `--story` to create a story-linked task. Use `--project` for floating tasks (bugs, hotfixes not part of a story).
- Status values for stories and tasks: `todo` | `in_progress` | `completed`. Steps have no status.
- **Story status is derived from its tasks and reconciled on every status mutation** — `tasks start`, `tasks complete`, `tasks update --status`, and `stories update --status` all trigger reconciliation. Rules: all tasks `completed` → story `completed`; all tasks `todo` → story `todo`; otherwise → story `in_progress`. A manual `stories update --status` value that disagrees with the task states is overridden.
- **There is no `stories delete` command.** To remove a story, delete all its tasks individually, then mark it completed via `stories update --status completed`.
- **Cleanup**: use `atm tasks delete <ID>` to remove a task and all its steps, or `atm steps delete <SEQ> --task <TASK_ID>` to remove a single step. Both confirm deletion as JSON. Only delete tasks or steps that have not been started.

## Task Sizing

A task is one coherent unit of deliverable work — a single feature addition, a focused bug fix, or a self-contained refactor of one component. Size tasks so a build agent can complete the work within a single context window without pausing for scope reasons.

**Too small:** The work is a step, not a task. If completing it takes under a few minutes or makes no independently meaningful change, it belongs inside a larger task.

**Too broad:** The work spans multiple subsystems or requires fundamentally different context mid-way through. Split it into multiple tasks or promote it to a story.

**Secondary signal:** 2–5 steps per task is a natural sizing check. Fewer than 2 suggests the task is too granular; more than 6 suggests it is too broad.

## Definition of Done

Tasks support an optional `definition_of_done` field — a JSON array of structured, verifiable acceptance criteria.

Each DoD item has three fields:
- `description` — what the criterion is
- `expected_outcome` — what a passing result looks like
- `exec` — command to run to verify (optional but strongly recommended)

**`exec` convention:** Append `&& echo 'OK'` to every exec command. This keeps the signal binary (exit code 0 = pass, non-zero = fail) and produces visible confirmation in logs without requiring output parsing. This convention anticipates a future hook that gates `tasks complete` by running all exec commands automatically.

**When to write a definition of done:**
- Write one for every task. A DoD makes handoff unambiguous: the build role knows exactly when the work is complete and has a mechanical way to verify it.
- Keep criteria concrete and testable. Avoid vague language — each item must be checkable by running its `exec` command or by inspection.

**How to write it:**
```bash
cat > /tmp/dod.json << 'EOF'
[
  {
    "description": "All unit tests pass",
    "expected_outcome": "pytest exits with code 0",
    "exec": "uv run pytest && echo 'OK'"
  },
  {
    "description": "No lint errors",
    "expected_outcome": "ruff reports no issues",
    "exec": "uv run ruff check . && echo 'OK'"
  }
]
EOF
atm tasks create --story <STORY_ID> --title "..." --description-file /tmp/desc.md --definition-of-done-file /tmp/dod.json
```
