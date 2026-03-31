# db.repo — Quick Reference

All functions are importable from `db.repo`. Every function takes an `Engine` as its first argument.

---

## Project

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `get_project` | `(engine, project_id: str)` | `Project \| None` | Eagerly loads stories → tasks → steps, and floating bugs/hotfixes |
| `list_projects` | `(engine)` | `list[Project]` | All projects, flat (no nested relations) |
| `list_active_projects` | `(engine)` | `list[Project]` | Projects where `status != COMPLETED` |

---

## Story

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_story` | `(engine, data: StoryCreate)` | `Story` | Auto-assigns next `seq` within the project |
| `get_story` | `(engine, story_id: str)` | `Story \| None` | Lookup by UUID |
| `get_story_by_seq` | `(engine, project_id: str, seq: int)` | `Story \| None` | Lookup by project-scoped seq |
| `list_stories` | `(engine, project_id: str)` | `list[Story]` | All stories ordered by seq |
| `list_active_stories` | `(engine, project_id: str)` | `list[Story]` | Stories where `status != COMPLETED`, ordered by seq |
| `update_story` | `(engine, story_id: str, data: StoryUpdate)` | `Story \| None` | Patches title, description, status |
| `delete_story` | `(engine, story_id: str)` | `bool` | Returns `False` if not found |

---

## Task

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_task` | `(engine, data: TaskCreate)` | `Task` | Seq scoped to story if `story_id` set, otherwise project-scoped (floating) |
| `get_task` | `(engine, task_id: str)` | `Task \| None` | Lookup by UUID |
| `get_task_by_seq` | `(engine, story_id: str, seq: int)` | `Task \| None` | Lookup by story-scoped seq |
| `get_floating_task_by_seq` | `(engine, project_id: str, seq: int)` | `Task \| None` | Lookup floating task (no story) by project-scoped seq |
| `list_floating_tasks` | `(engine, project_id: str)` | `list[Task]` | Tasks with no parent story, ordered by seq |
| `update_task` | `(engine, task_id: str, data: TaskUpdate)` | `Task \| None` | Patches title, description, status, prefix |
| `delete_task` | `(engine, task_id: str)` | `bool` | Returns `False` if not found |

---

## Step

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_step` | `(engine, data: StepCreate)` | `Step` | Auto-assigns next `seq` within the task |
| `get_step` | `(engine, step_id: str)` | `Step \| None` | Lookup by UUID |
| `get_step_by_seq` | `(engine, task_id: str, seq: int)` | `Step \| None` | Lookup by task-scoped seq |
| `get_next_step` | `(engine, task_id: str)` | `Step \| None` | First `TODO` step in the task, ordered by seq |
| `update_step` | `(engine, step_id: str, data: StepUpdate)` | `Step \| None` | Patches title, description, status |
| `delete_step` | `(engine, step_id: str)` | `bool` | Returns `False` if not found |

---

## Completion

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_completion` | `(engine, data: CompletionCreate)` | `Completion` | Records an agent action against any entity |
| `list_completions_by_entity` | `(engine, entity_id: str)` | `list[Completion]` | All completion records for one entity, ordered by `created_at` |
| `list_completions_for_entities` | `(engine, entity_ids: list[str])` | `list[Completion]` | Bulk fetch for multiple entity IDs, ordered by `created_at` |
| `list_active_assignments` | `(engine)` | `list[Completion]` | Entities whose latest completion record has `action=STARTED` |
