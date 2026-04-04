---
name: atm:dev-agent
description: ATM skill for the Dev agent. Executes work by picking up tasks, claiming steps, and marking them complete.
---

# ATM Dev Agent

The Dev agent executes work. It picks up tasks, works through steps sequentially, and records completion.

Load the common foundation first: `/atm`

## Dev-Only Commands

| Command | Purpose |
|---|---|
| `uv run atm steps next --task <TASK_ID>` | Get the next pending (TODO) step for a task |
| `uv run atm steps start <STEP_ID> --agent <AGENT_NAME> --session <SESSION_ID> [--branch BRANCH]` | Claim a step as in-progress |
| `uv run atm steps complete <STEP_ID> --agent <AGENT_NAME> --session <SESSION_ID> [--branch BRANCH]` | Mark a step done (cascades to task/story if all steps complete) |

## Workflow

1. **Receive task export** — the agent is given a self-contained markdown export (produced by `atm-admin tasks export <TASK_ID>`). This document contains the task ID, description, and all steps with their IDs and implementation descriptions. No further CLI queries are needed to understand the work.
2. **Get next pending step** → `steps next --task <TASK_ID>`
3. **Claim step** → `steps start <STEP_ID> --agent <AGENT_NAME> --session $ATM_SESSION_ID [--branch <BRANCH>]`
4. **Do the work**
5. **Complete step** → `steps complete <STEP_ID> --agent <AGENT_NAME> --session $ATM_SESSION_ID [--branch <BRANCH>]`
6. **Repeat steps 2–5** until `steps next` returns `not_found` (all steps done)

## Initialization

The Dev agent is either:
- Given a task export markdown by the caller → go to step 2 using the task ID from the export
- Discovering incomplete work → use `completions active` to find in-progress assignments

## Notes

- Always pass your agent name (provided by your caller) as `--agent`.
- Always pass `$ATM_SESSION_ID` as `--session`.
- `steps complete` cascades: if all steps in a task are complete, the task is marked completed. If all tasks in a story are complete, the story is marked completed.
- A step must be in `todo` status to be started. A step must be in `in_progress` to be completed.
- `steps next` returns `{"error": "not_found", ...}` when no pending steps remain — that signals the task is fully executed.
