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
| `uv run atm stories create --project <PROJECT_ID> --title <TITLE> --description <DESC>` | Create a new story |
| `uv run atm stories update <ID> [--title TITLE] [--description DESC] [--status STATUS]` | Update story fields or status |
| `uv run atm tasks create --story <STORY_ID> --title <TITLE> --description <DESC>` | Create a task under a story |
| `uv run atm tasks create --project <PROJECT_ID> --title <TITLE> --description <DESC> [--prefix PREFIX]` | Create a floating task (bug, hotfix) |
| `uv run atm tasks update <ID> [--title TITLE] [--description DESC] [--status STATUS] [--prefix PREFIX]` | Update task fields |
| `uv run atm tasks list-floating --project <PROJECT_ID>` | List floating tasks |
| `uv run atm steps create --task <TASK_ID> --title <TITLE> --description <DESC>` | Define a step within a task |
| `uv run atm steps get <SEQ> --task <TASK_ID>` | Fetch step details |

## Workflow

1. **Load project context** → `projects get <PROJECT_ID>`
2. **Review existing stories** → `stories list --project <PROJECT_ID>`
3. **Create or update stories** → `stories create` / `stories update`
4. **Decompose stories into tasks** → `tasks create --story <STORY_ID> ...`
5. **Define steps for each task** → `steps create --task <TASK_ID> ...` (one step per discrete unit of work)
6. **Monitor progress** → `completions active` / `completions list --entity <ENTITY_ID>`

## Notes

- Tasks must be decomposed into steps before a Dev agent can execute them. A task with no steps cannot be started.
- Use `--story` to create a story-linked task. Use `--project` for floating tasks (bugs, hotfixes not part of a story).
- Status values for stories and tasks: `todo` | `in_progress` | `completed`
