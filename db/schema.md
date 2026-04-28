# Information Model

## Overview

Five tables. `projects` is the root. Stories and tasks hang off projects.
Steps always hang off tasks. Completions log every state transition across all three
entity types.

Work is addressed as `x.y.z` — story seq, task seq, step seq. Floating tasks
(no parent story) use a letter prefix instead of a story number: `b.2.3` is step 3
of bug task 2, `h.1.4` is step 4 of hotfix task 1. All IDs are UUIDs assigned by
the application layer. Sequence numbers are also application-assigned and used
for addressing only — never as primary keys.

All timestamps are ISO 8601 strings (e.g. `2026-03-21T14:32:00Z`), application-assigned.
SQLite has no native timestamp type; this format keeps the schema portable to Postgres.

---

## projects

| Column      | Type    | Constraints                                                                   |
|-------------|---------|-------------------------------------------------------------------------------|
| id          | TEXT    | PK, UUID                                                                      |
| title       | TEXT    | NOT NULL                                                                      |
| description | TEXT    | NOT NULL                                                                      |
| status      | TEXT    | NOT NULL, CHECK(status IN ('TODO','IN_PROGRESS','COMPLETED')), DEFAULT 'TODO' |
| created_at  | TEXT    | NOT NULL, ISO 8601                                                            |
| updated_at  | TEXT    | NOT NULL, ISO 8601                                                            |

The root of the hierarchy. All stories and floating tasks belong to a project.

---

## stories

| Column      | Type    | Constraints                                                                   |
|-------------|---------|-------------------------------------------------------------------------------|
| id          | TEXT    | PK, UUID                                                                      |
| seq         | INTEGER | NOT NULL                                                                      |
| project_id  | TEXT    | FK → projects.id, NOT NULL                                                    |
| title       | TEXT    | NOT NULL                                                                      |
| description | TEXT    | NOT NULL                                                                      |
| status      | TEXT    | NOT NULL, CHECK(status IN ('TODO','IN_PROGRESS','COMPLETED')), DEFAULT 'TODO' |
| created_at  | TEXT    | NOT NULL, ISO 8601                                                            |
| updated_at  | TEXT    | NOT NULL, ISO 8601                                                            |

A story is a meaningful unit of work scoped to a single outcome within a project.
`seq` is scoped per project. Renders as the `x` in `x.y.z`.

Description should provide enough context for a planning agent to decompose
the story into tasks and steps without further input.

Story status is **derived from its tasks** and reconciled on every task or story
status mutation:

- All tasks `COMPLETED` → story `COMPLETED`
- All tasks `TODO` → story `TODO`
- Otherwise (any `IN_PROGRESS`, or a mix) → story `IN_PROGRESS`

A story with no tasks keeps whatever status was set manually. Direct
`stories update --status` calls are accepted and then reconciled — manual values
are overridden when they disagree with the task states.

---

## tasks

| Column      | Type    | Constraints                                                                   |
|-------------|---------|-------------------------------------------------------------------------------|
| id          | TEXT    | PK, UUID                                                                      |
| seq         | INTEGER | NOT NULL                                                                      |
| project_id  | TEXT    | FK → projects.id, NOT NULL                                                    |
| story_id    | TEXT    | FK → stories.id, nullable                                                     |
| prefix      | TEXT    | nullable, single letter, e.g. 'b' (bug), 'h' (hotfix)                        |
| title       | TEXT    | NOT NULL                                                                      |
| description | TEXT    | NOT NULL                                                                      |
| status      | TEXT    | NOT NULL, CHECK(status IN ('TODO','IN_PROGRESS','COMPLETED')), DEFAULT 'TODO' |
| created_at  | TEXT    | NOT NULL, ISO 8601                                                            |
| updated_at  | TEXT    | NOT NULL, ISO 8601                                                            |

A task belongs to a story, or floats (story_id NULL) for unplanned work such as
bugs or hotfixes. Floating tasks still belong to a project.

`prefix` is only set on floating tasks. A NULL prefix on a floating task is valid
but undisplayed. Known prefixes: `b` = bug, `h` = hotfix. All other letters are
permitted but undocumented.

`seq` is scoped to the parent story. For floating tasks, seq is scoped per project
among other floating tasks. Rendering: standard tasks show as `x.y`, floating tasks
show as `<prefix>.y` (e.g. `b.2`).

The task is the unit at which lifecycle status is tracked. Mutating a task's
status (via `tasks start`, `tasks complete`, or `tasks update --status`) triggers
reconciliation of the parent story's status.

---

## steps

| Column      | Type    | Constraints                                                                   |
|-------------|---------|-------------------------------------------------------------------------------|
| id          | TEXT    | PK, UUID                                                                      |
| seq         | INTEGER | NOT NULL                                                                      |
| task_id     | TEXT    | FK → tasks.id, NOT NULL                                                       |
| title       | TEXT    | NOT NULL                                                                      |
| description | TEXT    | NOT NULL                                                                      |
| created_at  | TEXT    | NOT NULL, ISO 8601                                                            |
| updated_at  | TEXT    | NOT NULL, ISO 8601                                                            |

Steps never float — they always belong to a task. Description is the direct
instruction to the coding agent for a single discrete unit of work.

`seq` is scoped to the parent task. Renders as the `z` in `x.y.z` or `<prefix>.y.z`.

Steps have **no lifecycle status**. They serve only as the planning agent's
ordered breakdown of how the build agent should sequence work within a task. The
build agent reads steps as a checklist and calls `tasks complete` once the work
is done; the parent task's status (and the story's, via cascade) is the single
source of truth for progress.

---


## completions

| Column      | Type    | Constraints                                                             |
|-------------|---------|-------------------------------------------------------------------------|
| id          | TEXT    | PK, UUID                                                                |
| entity_type | TEXT    | NOT NULL, CHECK(entity_type IN ('story','task','step'))                 |

| entity_id   | TEXT    | NOT NULL                                                                |
| action      | TEXT    | NOT NULL, CHECK(action IN ('started','completed'))                      |
| agent_name  | TEXT    | NOT NULL                                                                |
| session_id  | TEXT    | NOT NULL                                                                |
| branch      | TEXT    | nullable                                                                |
| created_at  | TEXT    | NOT NULL, ISO 8601                                                      |
| updated_at  | TEXT    | NOT NULL, ISO 8601                                                      |

A log of every state transition across stories, tasks, and steps. One row per event.
`entity_id` is a UUID referencing the relevant table determined by `entity_type`.

`branch` is nullable — not all completions occur in a branch context. Branch activity
at the task or story level can be inferred by querying completions by entity — no need
to store branch on the entities themselves.

This table is the source of truth for who did what and when. The GUI derives kanban
state and activity timelines from this log. The status columns on the entity tables
are the current snapshot; completions is the full history.
