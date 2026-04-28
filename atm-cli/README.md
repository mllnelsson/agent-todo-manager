# atm-cli

Command-line interface for the Agent Todo Manager. Provides AI agents with the ability to read and manipulate projects, stories, tasks, steps, and completions.

## Agent roles

The CLI is role-agnostic — any agent can call any command. By convention, two roles are expected:

**PM agent** — responsible for planning and structure:
- Create and delete stories
- Create and delete tasks
- Update story and task status during replanning

**Worker agent** — responsible for execution:
- Claim a task with `tasks start`
- Work through the task's steps in order — steps are a sequencing checklist with no per-step state
- Create or delete steps when breaking down or recovering from mistakes
- Mark the task done with `tasks complete`; the story's status is reconciled automatically
