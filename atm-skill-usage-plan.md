# ATM Skill Usage Plan

## Overview

Two skill files that describe the behaviour for the two agent personas that interact with `atm-cli`: the **PM agent** (plans and creates work) and the **Dev agent** (executes work).

Skill files are stored as resources in `resources/skills/` for users to copy into their own setup.

## Environment Variables

Both agents expect the following env vars:

| Variable | Required | Description |
|---|---|---|
| `ATM_PROJECT_ID` | Yes | Default project UUID. Commands that accept `--project` can override it. Raise if empty and no override supplied. |
| `ATM_AGENT_NAME` | Yes | Agent identity (e.g. `pm`, `dev`). Used in `steps start` / `steps complete`. |
| `ATM_SESSION_ID` | Yes | Session UUID. Set by whoever spawns the agent. Used for completion tracking. |

## PM Agent (`resources/skills/pm-agent.md`)

**Role:** Plans and structures work. Owns the hierarchy creation.

**Commands:**

| Command | Purpose |
|---|---|
| `atm projects get` | Load project context |
| `atm stories list --project` | List active stories |
| `atm stories get` | Fetch a story by UUID or seq |
| `atm stories create --project --title --description` | Create a new story |
| `atm stories update` | Update story fields/status |
| `atm tasks create --story/--project --title --description` | Create tasks under stories or as floating (bug/hotfix) |
| `atm tasks get` | Fetch task details |
| `atm tasks update` | Update task fields/status |
| `atm tasks list-floating --project` | List floating tasks (bugs, hotfixes) |
| `atm steps create --task --title --description` | Define steps within a task |
| `atm steps get` | Fetch step details |
| `atm completions list --entity` | Check completion history for an entity |
| `atm completions active` | See all active assignments |

**Workflow:** Get project -> create/review stories -> decompose into tasks -> define steps for each task -> monitor progress via completions.

## Dev Agent (`resources/skills/dev-agent.md`)

**Role:** Executes work. Picks up tasks and works through steps.

**Commands:**

| Command | Purpose |
|---|---|
| `atm tasks get --md` | Understand what needs doing (task + step overview) |
| `atm steps next --task` | Get the next pending (TODO) step |
| `atm steps start --agent --session [--branch]` | Claim a step as in-progress |
| `atm steps complete --agent --session [--branch]` | Mark step done (cascades to task/story) |
| `atm completions active` | See current assignments |

**Workflow:** Get task -> get next step -> start -> do work -> complete -> repeat until task done.

**Initialization:** The dev agent is either given a task ID directly, or discovers incomplete work via `atm tasks get`.

## Project ID Handling

- On any command that requires a project ID: read from `ATM_PROJECT_ID` env var.
- If a `--project` flag is explicitly supplied, use that instead (override).
- If neither is available, raise an error.
