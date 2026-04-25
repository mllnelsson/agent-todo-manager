---
name: core
description: Common foundation for ATM CLI usage. Covers environment setup, project ID resolution, and commands shared by both plan and build roles.
---

# ATM CLI — Common Foundation

The `atm` CLI manages a hierarchy of project → story → task → step. Load this skill as the common base for both plan and build roles.

## Environment

| Variable | Required | Description |
|---|---|---|
| `ATM_PROJECT_ID` | Yes | Default project UUID. Commands that accept `--project` use this unless overridden. Raise an error if empty and no `--project` flag is supplied. |
| `ATM_SESSION_ID` | Yes | Session UUID. Set by whoever spawns the session. Passed to `steps start` and `steps complete`. |

## Identity

Your caller provides your name (e.g. `plan`, `build`). Pass it as the `--agent` flag when calling `tasks start`, `tasks complete`, `steps start`, and `steps complete`.

## Project ID Handling

- On any command that accepts `--project`: use `ATM_PROJECT_ID` from the environment.
- If `--project` is explicitly supplied, use that value instead.
- If neither is available, raise an error — do not proceed.

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
