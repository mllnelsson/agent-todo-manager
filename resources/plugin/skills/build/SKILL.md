---
name: build
description: ATM skill for executing work — picking up tasks, working through their steps, and marking the task complete.
---

# ATM Build

Load this skill to execute work. It covers picking up a task, working through its steps in order, and recording completion.

Load the common foundation first: `/atm:core`

## Commands

### Retrieval (delegate to `atm-lookup`)

| Command | Purpose |
|---|---|
| `atm tasks get` | Fetch the task (with its steps) as JSON — see cli-reference.md for full syntax |

### Mutations (run directly)

| Command | Purpose |
|---|---|
| `atm tasks start <TASK_ID> [--branch BRANCH]` | Claim a task as in-progress (cascades story status) |
| `atm tasks complete <TASK_ID> [--branch BRANCH]` | Mark the task done (cascades story status) |

`--agent` and `--session` default from the environment (`$ATM_AGENT_NAME`, `$ATM_SESSION_ID`) — do not pass them unless overriding. See `/atm:core` for details.

## Workflow

1. **Receive a task ID** from the caller. Delegate to `atm-lookup` to fetch the task details (description, definition of done, ordered steps).
2. **Claim the task** → `tasks start <TASK_ID> [--branch <BRANCH>]`
3. **Work through the steps in order.** Steps are a sequencing checklist from the planning agent — there is no per-step state to set. Treat each step's description as the immediate instruction; finish it before moving to the next.
4. **Verify the task definition of done** before completing. If criteria are not met, keep working until they are.
5. **Complete the task** → `tasks complete <TASK_ID> [--branch <BRANCH>]`. This cascades to the story (if all sibling tasks are done, the story is also marked completed).

## Notes

- **Steps have no status** — there is no `steps start`, `steps complete`, or `steps next`. The single completion signal for the build role is `tasks complete`.
- A task must be in `todo` to be started and `in_progress` to be completed.
- **Definition of done is a hard gate** — every criterion in the task's `definition_of_done` must be satisfied before calling `tasks complete`. Never mark work complete on the assumption that criteria will be met later.
- **Run `exec` commands to verify mechanically** — each DoD item may carry an `exec` field. Run it and check the exit code: 0 = pass, non-zero = fail. Do not call `tasks complete` until all exec commands exit 0.
