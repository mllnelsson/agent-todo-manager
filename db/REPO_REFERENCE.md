# db.repo — Quick Reference

All functions are importable from `db.repo`. Every function takes an `Engine` as its first argument.

---

> **Lazy vs eager loading:** List functions return shallow models with empty child lists (`stories/tasks/steps = []`). Get-by-id and get-by-seq functions eager-load all children.

## Project

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `get_project` | `(engine, project_id: str)` | `Project \| None` | Full: stories → tasks → steps, floating bugs/hotfixes |
| `list_projects` | `(engine)` | `list[Project]` | Shallow — no nested relations |
| `list_active_projects` | `(engine)` | `list[Project]` | Shallow — `status != COMPLETED` |

---

## Story

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_story` | `(engine, data: StoryCreate)` | `Story` | Auto-assigns next `seq` within the project |
| `get_story` | `(engine, story_id: str)` | `Story \| None` | Full: tasks → steps, lookup by UUID |
| `get_story_by_seq` | `(engine, project_id: str, seq: int)` | `Story \| None` | Full: tasks → steps, lookup by project-scoped seq |
| `list_stories` | `(engine, project_id: str)` | `list[Story]` | Shallow — ordered by seq |
| `list_active_stories` | `(engine, project_id: str)` | `list[Story]` | Shallow — `status != COMPLETED`, ordered by seq |
| `update_story` | `(engine, story_id: str, data: StoryUpdate)` | `Story \| None` | Patches title, description, status. The service layer (`update_story_by_id`) reconciles status from tasks after applying the patch. |
| `delete_story` | `(engine, story_id: str)` | `bool` | Returns `False` if not found |

---

## Task

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_task` | `(engine, data: TaskCreate)` | `Task` | Seq scoped to story if `story_id` set, otherwise project-scoped (floating) |
| `get_task` | `(engine, task_id: str)` | `Task \| None` | Full: steps, lookup by UUID |
| `get_task_by_seq` | `(engine, story_id: str, seq: int)` | `Task \| None` | Full: steps, lookup by story-scoped seq |
| `get_floating_task_by_seq` | `(engine, project_id: str, seq: int)` | `Task \| None` | Full: steps, lookup floating task by project-scoped seq |
| `list_floating_tasks` | `(engine, project_id: str)` | `list[Task]` | Shallow — tasks with no parent story, ordered by seq |
| `update_task` | `(engine, task_id: str, data: TaskUpdate)` | `Task \| None` | Patches title, description, status, prefix. The service layer (`update_task_by_id`) reconciles the parent story's status when `status` is patched. |
| `delete_task` | `(engine, task_id: str)` | `bool` | Returns `False` if not found |

---

## Step

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_step` | `(engine, data: StepCreate)` | `Step` | Auto-assigns next `seq` within the task |
| `get_step` | `(engine, step_id: str)` | `Step \| None` | Lookup by UUID |
| `get_step_by_seq` | `(engine, task_id: str, seq: int)` | `Step \| None` | Lookup by task-scoped seq |
| `update_step` | `(engine, step_id: str, data: StepUpdate)` | `Step \| None` | Patches title, description, definition_of_done. Steps have no status. |
| `delete_step` | `(engine, step_id: str)` | `bool` | Returns `False` if not found |

---

## Completion

| Function | Signature | Returns | Notes |
|---|---|---|---|
| `create_completion` | `(engine, data: CompletionCreate)` | `Completion` | Records an agent action against any entity |
| `list_completions_by_entity` | `(engine, entity_id: str)` | `list[Completion]` | All completion records for one entity, ordered by `created_at` |
| `list_completions_for_entities` | `(engine, entity_ids: list[str])` | `list[Completion]` | Bulk fetch for multiple entity IDs, ordered by `created_at` |
| `list_active_assignments` | `(engine)` | `list[Completion]` | Entities whose latest completion record has `action=STARTED` |
