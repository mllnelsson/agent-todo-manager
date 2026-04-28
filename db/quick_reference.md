# Schema Quick Reference

## projects
(**id**, title, description, status, created_at, updated_at)
 
## stories
(**id**, seq, project_id→projects, title, description, status, created_at, updated_at)
 
## tasks
(**id**, seq, project_id→projects, story_id→stories, prefix, title, description, status, created_at, updated_at)
 
## steps
(**id**, seq, task_id→tasks, title, description, created_at, updated_at)
 

## completions
(**id**, entity_type, entity_id, action, agent_name, session_id, branch, created_at, updated_at)

---
## Reference Key
**bold** = primary key  
`→` = foreign key reference  
`story_id` is nullable — floating tasks belong to a project but not a story  
`task_id` is NOT NULL — steps always have a parent task  
`prefix` is nullable — null means standard story task, letter value means special type
`created_at` / `updated_at` — ISO 8601 strings, application-assigned  
---
## Full Schema
Full schema can be found in the [Schema Defintion](./schema.md)
