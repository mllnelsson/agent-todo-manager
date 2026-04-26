---
name: core
description: Common foundation for ATM CLI usage. Covers environment setup, project ID resolution, and commands shared by both plan and build roles.
---

# ATM CLI — Common Foundation

The `atm` CLI manages a hierarchy of project → story → task → step. Load this skill as the common base for both plan and build roles.

## Environment (set automatically by the SessionStart hook)

| Variable | Set by | Read by |
|---|---|---|
| `ATM_PROJECT_ID` | hook (reads `<repo-root>/.atm_project_id`) | every command that accepts `--project` |
| `ATM_SESSION_ID` | hook | `tasks start` / `tasks complete` / `steps start` / `steps complete` |
| `ATM_AGENT_NAME` | hook | `tasks start` / `tasks complete` / `steps start` / `steps complete` |

## Calling the CLI

**Do not pass `--project`, `--session`, or `--agent` yourself.** The CLI reads them from the environment. Passing them manually is reserved for the rare case where you must override the session-default project (e.g. acting on a different project from the same shell).

If a command errors with something like "`--project` not provided and `ATM_PROJECT_ID` is not set", treat it as a setup bug — do not work around it by hard-coding a UUID into the flag. Check that `<repo-root>/.atm_project_id` exists and contains the project UUID.

## Invocation

```
atm [COMMAND_GROUP] [SUBCOMMAND] [FLAGS]
```

## Shared Commands

| Command | Purpose |
|---|---|
| `atm projects get <PROJECT_ID>` | Load project context |
| `atm tasks get <ID_OR_SEQ> [--story STORY_ID] [--project PROJECT_ID]` | Fetch task details as JSON |
| `atm completions active` | List all active in-progress step assignments |
| `atm completions list --entity <ENTITY_ID>` | Check completion history for a specific entity |

## Output

- **Success:** JSON to stdout (nulls excluded)
- **Error:** `{"error": "<code>", "context": "<message>"}` to stdout
- **Exit codes:** `0` = success, `1` = user error, `2` = system error

## Full CLI Reference

See `resources/cli-reference.md` for the complete man-page-style reference covering every command's arguments, options, and notes.

## Role Skills

- **Plan** → `plan/SKILL.md` (`/atm:core:plan`)
- **Build** → `build/SKILL.md` (`/atm:core:build`)
