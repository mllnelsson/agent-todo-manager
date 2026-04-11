---
name: atm
description: Common foundation for ATM CLI agents. Covers environment setup, project ID resolution, and commands used by both PM and Dev roles.
---

# ATM CLI — Common Foundation

The `atm` CLI manages a hierarchy of project → story → task → step. Both PM and Dev agents use this skill as their common base.

## Environment

| Variable | Required | Description |
|---|---|---|
| `ATM_PROJECT_ID` | Yes | Default project UUID. Commands that accept `--project` use this unless overridden. Raise an error if empty and no `--project` flag is supplied. |
| `ATM_SESSION_ID` | Yes | Session UUID. Set by whoever spawns the agent. Passed to `steps start` and `steps complete`. |

## Agent Name

Your caller provides your agent name (e.g. `pm`, `dev`). Pass it as the `--agent` flag when calling `tasks start`, `tasks complete`, `steps start`, and `steps complete`.

## Project ID Handling

- On any command that accepts `--project`: use `ATM_PROJECT_ID` from the environment.
- If `--project` is explicitly supplied, use that value instead.
- If neither is available, raise an error — do not proceed.

## Invocation

```
uv run atm [COMMAND_GROUP] [SUBCOMMAND] [FLAGS]
```

## Shared Commands

Both agents use these commands:

| Command | Purpose |
|---|---|
| `uv run atm projects get <PROJECT_ID>` | Load project context |
| `uv run atm tasks get <ID_OR_SEQ> [--story STORY_ID] [--project PROJECT_ID]` | Fetch task details as JSON |
| `uv run atm completions active` | List all active in-progress step assignments |
| `uv run atm completions list --entity <ENTITY_ID>` | Check completion history for a specific entity |

## Output

- **Success:** JSON to stdout (nulls excluded)
- **Error:** `{"error": "<code>", "context": "<message>"}` to stdout
- **Exit codes:** `0` = success, `1` = user error, `2` = system error

## Full CLI Reference

See `resources/cli-reference.md` for the complete man-page-style reference covering every command's arguments, options, and notes.

## Agent Skills

- **PM Agent** → `pm-agent/SKILL.md` (`/atm:pm-agent`)
- **Dev Agent** → `dev-agent/SKILL.md` (`/atm:dev-agent`)
