---
name: build
description: ATM skill for executing work — picking up tasks, working through their steps, and marking the task complete.
---

# ATM Build

Load this skill to execute work. It covers picking up a task, working through its steps in order, and recording completion.

Load the common foundation first: `/atm:core`

## Commands

| Command | Purpose |
|---|---|
| `atm tasks get <ID_OR_SEQ> [--story STORY_ID] [--project PROJECT_ID]` | Fetch the task (with its steps) as JSON |
| `atm tasks start <TASK_ID> --agent <AGENT_NAME> --session <SESSION_ID> [--branch BRANCH]` | Claim a task as in-progress (cascades story status) |
| `atm tasks complete <TASK_ID> --agent <AGENT_NAME> --session <SESSION_ID> [--branch BRANCH]` | Mark the task done (cascades story status) |

## Workflow

1. **Receive task export** — a self-contained markdown export containing the task ID, description, definition of done, and the ordered list of steps with their descriptions. No further CLI queries are needed to understand the work.
2. **Claim the task** → `tasks start <TASK_ID> --agent <AGENT_NAME> --session $ATM_SESSION_ID [--branch <BRANCH>]`
3. **Work through the steps in order.** Steps are a sequencing checklist from the planning agent — there is no per-step state to set. Treat each step's description as the immediate instruction; finish it before moving to the next.
4. **Verify each step's definition of done** as you go. If a step has a `definition_of_done`, every criterion must be satisfied before progressing.
5. **Verify the task definition of done** before completing. If criteria are not met, keep working until they are.
6. **Complete the task** → `tasks complete <TASK_ID> --agent <AGENT_NAME> --session $ATM_SESSION_ID [--branch <BRANCH>]`. This cascades to the story (if all sibling tasks are done, the story is also marked completed).

## Initialization

Either:
- Given a task export markdown by the caller → use the task ID from the export
- Discovering incomplete work → use `completions active` to find in-progress assignments

## Notes

- Always pass your name (provided by your caller) as `--agent`.
- Always pass `$ATM_SESSION_ID` as `--session`.
- **Steps have no status** — there is no `steps start`, `steps complete`, or `steps next`. The single completion signal for the build role is `tasks complete`.
- A task must be in `todo` to be started and `in_progress` to be completed.
- **Definition of done is a hard gate** — every criterion in the task's `definition_of_done` must be satisfied before calling `tasks complete`. Never mark work complete on the assumption that criteria will be met later.
- **Run `exec` commands to verify mechanically** — each DoD item may carry an `exec` field. Run it and check the exit code: 0 = pass, non-zero = fail. Do not call `tasks complete` until all exec commands exit 0. Steps retain a freetext `definition_of_done` — verify those by inspection.
