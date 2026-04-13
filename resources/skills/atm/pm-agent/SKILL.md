---
name: atm:pm-agent
description: ATM skill for the PM agent. Plans and structures work — owns hierarchy creation (stories, tasks, steps).
---

# ATM PM Agent

The PM agent plans and structures work. It creates and organises the hierarchy that Dev agents then execute.

Load the common foundation first: `/atm`

## PM-Only Commands

| Command | Purpose |
|---|---|
| `uv run atm stories list --project <PROJECT_ID>` | List active stories |
| `uv run atm stories get <ID_OR_SEQ> [--project PROJECT_ID]` | Fetch a story by UUID or seq |
| `uv run atm stories create --project <PROJECT_ID> --title <TITLE> --description-file <PATH>` | Create a new story |
| `uv run atm stories update <ID> [--title TITLE] [--description-file PATH] [--status STATUS]` | Update story fields or status |
| `uv run atm tasks create --story <STORY_ID> --title <TITLE> --description-file <PATH> [--definition-of-done-file PATH]` | Create a task under a story |
| `uv run atm tasks create --project <PROJECT_ID> --title <TITLE> --description-file <PATH> [--prefix PREFIX] [--definition-of-done-file PATH]` | Create a floating task (bug, hotfix) |
| `uv run atm tasks update <ID> [--title TITLE] [--description-file PATH] [--status STATUS] [--prefix PREFIX] [--definition-of-done-file PATH]` | Update task fields |
| `uv run atm tasks list-floating --project <PROJECT_ID>` | List floating tasks |
| `uv run atm steps create --task <TASK_ID> --title <TITLE> --description-file <PATH> [--definition-of-done-file PATH]` | Define a step within a task |
| `uv run atm steps get <SEQ> --task <TASK_ID>` | Fetch step details |

## Workflow

1. **Load project context** → `projects get <PROJECT_ID>`
2. **Review existing stories** → `stories list --project <PROJECT_ID>`
3. **Create or update stories** → `stories create` / `stories update`
4. **Decompose stories into tasks** → `tasks create --story <STORY_ID> ...`
5. **Define steps for each task** → `steps create --task <TASK_ID> ...` (one step per discrete unit of work)
6. **Monitor progress** → `completions active` / `completions list --entity <ENTITY_ID>`

## Notes

- Tasks must have at least one step defined before a Dev agent can pick them up. Always create steps for every task before handoff.
- The step **description** is the implementation specification — it should contain enough detail for a dev agent to complete the step without further questions. Write descriptions as clear, actionable instructions.
- Always use `--description-file` rather than `--description` for descriptions (and `--definition-of-done-file` rather than `--definition-of-done`). Write the content to a tempfile first, then pass the path. This avoids shell escaping issues with long text, newlines, and special characters: `cat > /tmp/desc.md << 'EOF' ... EOF && uv run atm steps create ... --description-file /tmp/desc.md`
- Use `--story` to create a story-linked task. Use `--project` for floating tasks (bugs, hotfixes not part of a story).
- Status values for stories and tasks: `todo` | `in_progress` | `completed`

## Definition of Done

Both tasks and steps support an optional `definition_of_done` field — explicit, verifiable acceptance criteria for that unit of work.

**When to write a definition of done:**
- Write one for every task and step. A DoD makes handoff unambiguous: the Dev agent knows exactly when the work is considered complete.
- Keep it concrete and testable. Avoid vague language — write criteria the Dev agent can check mechanically (e.g. "all tests pass", "endpoint returns 200 with schema X", "no lint errors").

**How to write it:**
```
cat > /tmp/dod.md << 'EOF'
- All unit tests for the new function pass
- The CLI command returns the correct JSON shape
- No ruff lint errors
EOF
uv run atm tasks create --story <STORY_ID> --title "..." --description-file /tmp/desc.md --definition-of-done-file /tmp/dod.md
```

Step-level DoD should be more granular than task-level — describe the specific outcome of that one implementation step.
