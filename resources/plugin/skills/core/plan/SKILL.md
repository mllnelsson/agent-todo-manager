---
name: core:plan
description: ATM skill for planning and structuring work — owns hierarchy creation (stories, tasks, steps).
---

# ATM Plan

Load this skill to plan and structure work. It covers creating and organising the project hierarchy that the build role then executes.

Load the common foundation first: `/atm:core`

## Commands

| Command | Purpose |
|---|---|
| `atm stories list --project <PROJECT_ID>` | List active stories |
| `atm stories get <ID_OR_SEQ> [--project PROJECT_ID]` | Fetch a story by UUID or seq |
| `atm stories create --project <PROJECT_ID> --title <TITLE> --description-file <PATH>` | Create a new story |
| `atm stories update <ID> [--title TITLE] [--description-file PATH] [--status STATUS]` | Update story fields or status |
| `atm tasks create --story <STORY_ID> --title <TITLE> --description-file <PATH> [--definition-of-done-file PATH]` | Create a task under a story |
| `atm tasks create --project <PROJECT_ID> --title <TITLE> --description-file <PATH> [--prefix PREFIX] [--definition-of-done-file PATH]` | Create a floating task (bug, hotfix) |
| `atm tasks update <ID> [--title TITLE] [--description-file PATH] [--status STATUS] [--prefix PREFIX] [--definition-of-done-file PATH]` | Update task fields |
| `atm tasks list-floating --project <PROJECT_ID>` | List floating tasks |
| `atm steps create --task <TASK_ID> --title <TITLE> --description-file <PATH> [--definition-of-done-file PATH]` | Define a step within a task |
| `atm steps get <SEQ> --task <TASK_ID>` | Fetch step details |

## Workflow

1. **Load project context** → `projects get <PROJECT_ID>`
2. **Review existing stories** → `stories list --project <PROJECT_ID>`
3. **Create or update stories** → `stories create` / `stories update`
4. **Decompose stories into tasks** → `tasks create --story <STORY_ID> ...`
5. **Define steps for each task** → `steps create --task <TASK_ID> ...` (one step per discrete unit of work)
6. **Monitor progress** → `completions active` / `completions list --entity <ENTITY_ID>`

## Notes

- **`stories list` returns story metadata only — no tasks.** To see a story's tasks, use `atm stories get <ID_OR_SEQ>`; the response embeds the full task array. There is no `tasks list --story` command.
- Tasks must have at least one step defined before the build role can pick them up. Always create steps for every task before handoff.
- The step **description** is the implementation specification — it should contain enough detail to complete the step without further questions. Write descriptions as clear, actionable instructions.
- Always use `--description-file` rather than `--description` for descriptions (and `--definition-of-done-file` rather than `--definition-of-done`). Write the content to a tempfile first, then pass the path. This avoids shell escaping issues with long text, newlines, and special characters: `cat > /tmp/desc.md << 'EOF' ... EOF && atm steps create ... --description-file /tmp/desc.md`
- Use `--story` to create a story-linked task. Use `--project` for floating tasks (bugs, hotfixes not part of a story).
- Status values for stories and tasks: `todo` | `in_progress` | `completed`
- **Story status cascades automatically.** Starting the first task of a `todo` story flips the story to `in_progress`; completing the last `in_progress` task of a story flips it to `completed`. Do not call `stories update --status` to drive these transitions.

## Definition of Done

Both tasks and steps support an optional `definition_of_done` field — explicit, verifiable acceptance criteria for that unit of work.

**When to write a definition of done:**
- Write one for every task and step. A DoD makes handoff unambiguous: the build role knows exactly when the work is considered complete.
- Keep it concrete and testable. Avoid vague language — write criteria that can be checked mechanically (e.g. "all tests pass", "endpoint returns 200 with schema X", "no lint errors").

**How to write it:**
```
cat > /tmp/dod.md << 'EOF'
- All unit tests for the new function pass
- The CLI command returns the correct JSON shape
- No ruff lint errors
EOF
atm tasks create --story <STORY_ID> --title "..." --description-file /tmp/desc.md --definition-of-done-file /tmp/dod.md
```

Step-level DoD should be more granular than task-level — describe the specific outcome of that one implementation step.
