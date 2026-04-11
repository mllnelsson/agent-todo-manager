# atm — CLI Reference

## NAME

`atm` — agent task manager for structured project work

## SYNOPSIS

```
uv run atm [COMMAND_GROUP] [SUBCOMMAND] [ARGUMENTS] [OPTIONS]
```

## DESCRIPTION

`atm` manages a four-level hierarchy: **project → story → task → step**.

- A **project** is the top-level container.
- A **story** groups related tasks under a project.
- A **task** is a discrete unit of work, either under a story or floating (not linked to a story).
- A **step** is an atomic action within a task, executed sequentially by a Dev agent.

**Completions** record when agents start or complete tasks and steps, providing an audit trail and active-assignment view.

Status values: `todo` | `in_progress` | `completed`

---

## COMMANDS

### projects

#### projects get

```
uv run atm projects get ID
```

Fetch a project by UUID and print it as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Project UUID |

---

### stories

#### stories list

```
uv run atm stories list --project PROJECT_ID
```

List all active stories for a project and print them as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--project` | string (UUID) | Yes | Project UUID |

---

#### stories get

```
uv run atm stories get ID_OR_SEQ [--project PROJECT_ID]
```

Fetch a story by UUID or project-scoped sequence number and print it as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID_OR_SEQ` | string | Yes | Story UUID, or integer sequence number |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--project` | string (UUID) | Conditional | Required when `ID_OR_SEQ` is a sequence number |

**Notes**

- There is no `tasks list --story` command. The story response includes all of the story's tasks as an embedded array — use `stories get` to list a story's tasks.

---

#### stories create

```
uv run atm stories create --project PROJECT_ID --title TITLE (--description DESCRIPTION | --description-file PATH)
```

Create a new story under a project and print it as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--project` | string (UUID) | Yes | Project UUID |
| `--title` | string | Yes | Story title |
| `--description` | string | Conditional | Story description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | Conditional | Path to a file containing the story description (mutually exclusive with `--description`) |

**Notes**

- Exactly one of `--description` or `--description-file` is required.
- Prefer `--description-file` when the description is long or contains special characters — write to a tempfile and pass the path.

---

#### stories update

```
uv run atm stories update ID [--title TITLE] [--description DESCRIPTION | --description-file PATH] [--status STATUS]
```

Update fields on a story and print the result as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Story UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--title` | string | No | New title |
| `--description` | string | No | New description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | No | Path to a file containing the new description (mutually exclusive with `--description`) |
| `--status` | string | No | New status: `todo` \| `in_progress` \| `completed` |

---

### tasks

#### tasks get

```
uv run atm tasks get ID_OR_SEQ [--story STORY_ID] [--project PROJECT_ID]
```

Fetch a task by UUID or sequence number and print it as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID_OR_SEQ` | string | Yes | Task UUID, or integer sequence number |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--story` | string (UUID) | Conditional | Required when `ID_OR_SEQ` is a seq for a story task |
| `--project` | string (UUID) | Conditional | Required when `ID_OR_SEQ` is a seq for a floating task |

**Notes**

- When using a sequence number, exactly one of `--story` or `--project` must be supplied.

---

#### tasks list-floating

```
uv run atm tasks list-floating --project PROJECT_ID
```

List all floating (story-less) tasks for a project and print them as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--project` | string (UUID) | Yes | Project UUID |

---

#### tasks create

```
uv run atm tasks create (--story STORY_ID | --project PROJECT_ID) --title TITLE (--description DESCRIPTION | --description-file PATH) [--prefix PREFIX]
```

Create a new task and print it as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--story` | string (UUID) | Conditional | Story UUID — use for story-linked tasks. Mutually exclusive with `--project`. |
| `--project` | string (UUID) | Conditional | Project UUID — use for floating tasks not linked to a story. Mutually exclusive with `--story`. |
| `--title` | string | Yes | Task title |
| `--description` | string | Conditional | Task description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | Conditional | Path to a file containing the task description (mutually exclusive with `--description`) |
| `--prefix` | string | No | Short prefix for floating tasks (e.g. `b` = bug, `h` = hotfix) |

**Notes**

- Exactly one of `--story` or `--project` is required.
- Exactly one of `--description` or `--description-file` is required.
- `--prefix` applies only to floating tasks (i.e. when `--project` is used).
- Prefer `--description-file` when the description is long or contains special characters — write to a tempfile and pass the path.

---

#### tasks update

```
uv run atm tasks update ID [--title TITLE] [--description DESCRIPTION | --description-file PATH] [--status STATUS] [--prefix PREFIX]
```

Update fields on a task and print the result as JSON. Does **not** write a completion record — use `tasks start` / `tasks complete` for status transitions that must be tracked.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Task UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--title` | string | No | New title |
| `--description` | string | No | New description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | No | Path to a file containing the new description (mutually exclusive with `--description`) |
| `--status` | string | No | New status: `todo` \| `in_progress` \| `completed` |
| `--prefix` | string | No | New prefix |

---

#### tasks start

```
uv run atm tasks start ID --agent AGENT_NAME --session SESSION_ID [--branch BRANCH]
```

Mark a task as `in_progress`, recording which agent claimed it. Prints the updated task as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Task UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--agent` | string | Yes | Name of the agent claiming the task |
| `--session` | string (UUID) | Yes | Agent session identifier (`$ATM_SESSION_ID`) |
| `--branch` | string | No | Git branch the agent is working on |

**Notes**

- The task must be in `todo` status. Starting an `in_progress` or `completed` task returns `invalid_status`.
- Use this for tasks without steps. For tasks with steps, use `steps start` on the individual steps instead.

---

#### tasks complete

```
uv run atm tasks complete ID --agent AGENT_NAME --session SESSION_ID [--branch BRANCH]
```

Mark a task as `completed`. Cascades: if the task belongs to a story and all tasks in that story are now done, the story is also marked completed. Prints the updated task as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Task UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--agent` | string | Yes | Name of the agent completing the task |
| `--session` | string (UUID) | Yes | Agent session identifier (`$ATM_SESSION_ID`) |
| `--branch` | string | No | Git branch the agent worked on |

**Notes**

- The task must be in `in_progress` status. Completing a `todo` or already `completed` task returns `invalid_status`.
- Use this for tasks without steps. For tasks with steps, completion cascades automatically via `steps complete`.

---

### steps

#### steps get

```
uv run atm steps get SEQ --task TASK_ID
```

Fetch a step by its task-scoped sequence number and print it as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `SEQ` | integer | Yes | Task-scoped sequence number of the step |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--task` | string (UUID) | Yes | Task UUID |

---

#### steps next

```
uv run atm steps next --task TASK_ID
```

Get the next pending (`todo`) step for a task and print it as JSON. Returns `{"error": "not_found", ...}` when no pending steps remain.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--task` | string (UUID) | Yes | Task UUID |

---

#### steps create

```
uv run atm steps create --task TASK_ID --title TITLE (--description DESCRIPTION | --description-file PATH)
```

Create a new step under a task and print it as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--task` | string (UUID) | Yes | Task UUID |
| `--title` | string | Yes | Step title |
| `--description` | string | Conditional | Step description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | Conditional | Path to a file containing the step description (mutually exclusive with `--description`) |

**Notes**

- Exactly one of `--description` or `--description-file` is required.
- Prefer `--description-file` when the description is long or contains special characters — write to a tempfile and pass the path.

---

#### steps update

```
uv run atm steps update ID [--title TITLE] [--description DESCRIPTION | --description-file PATH]
```

Update fields on a step and print the result as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Step UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--title` | string | No | New title |
| `--description` | string | No | New description (mutually exclusive with `--description-file`) |
| `--description-file` | string (path) | No | Path to a file containing the new description (mutually exclusive with `--description`) |

**Notes**

- Status cannot be changed via `update`. Use `steps start` and `steps complete` instead.

---

#### steps start

```
uv run atm steps start ID --agent AGENT_NAME --session SESSION_ID [--branch BRANCH]
```

Mark a step as `in_progress`, recording which agent claimed it. Prints the updated step as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Step UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--agent` | string | Yes | Name of the agent claiming the step |
| `--session` | string (UUID) | Yes | Agent session identifier (`$ATM_SESSION_ID`) |
| `--branch` | string | No | Git branch the agent is working on |

**Notes**

- The step must be in `todo` status. Starting an `in_progress` or `completed` step returns `invalid_status`.

---

#### steps complete

```
uv run atm steps complete ID --agent AGENT_NAME --session SESSION_ID [--branch BRANCH]
```

Mark a step as `completed`. Cascades: if all steps in the task are done, the task is marked completed; if all tasks in the story are done, the story is marked completed. Prints the updated step as JSON.

**Arguments**

| Name | Type | Required | Description |
|---|---|---|---|
| `ID` | string (UUID) | Yes | Step UUID |

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--agent` | string | Yes | Name of the agent completing the step |
| `--session` | string (UUID) | Yes | Agent session identifier (`$ATM_SESSION_ID`) |
| `--branch` | string | No | Git branch the agent worked on |

**Notes**

- The step must be in `in_progress` status. Completing a `todo` or already `completed` step returns `invalid_status`.

---

### completions

#### completions list

```
uv run atm completions list --entity ENTITY_ID
```

List all completion records for an entity (story, task, or step) and print them as JSON.

**Options**

| Flag | Type | Required | Description |
|---|---|---|---|
| `--entity` | string (UUID) | Yes | UUID of the entity (story, task, or step) |

---

#### completions active

```
uv run atm completions active
```

List all active assignments (steps currently `in_progress`) with agent and session info. Prints as JSON.

**Options**

None.

---

## ENVIRONMENT

| Variable | Required | Description |
|---|---|---|
| `ATM_PROJECT_ID` | Yes | Default project UUID used by commands that accept `--project` |
| `ATM_SESSION_ID` | Yes | Session UUID set by the agent spawner; passed to `tasks start` / `tasks complete` / `steps start` / `steps complete` |

## INPUTS

| Input | Description |
|---|---|
| Agent name | Identity string (e.g. `pm`, `dev`). Provided by the caller when spawning the agent. Used as `--agent` on `tasks start` / `tasks complete` / `steps start` / `steps complete`. |

## SEE ALSO

- `SKILL.md` — common foundation (`/atm`)
- `pm-agent/SKILL.md` — PM agent workflow (`/atm:pm-agent`)
- `dev-agent/SKILL.md` — Dev agent workflow (`/atm:dev-agent`)
