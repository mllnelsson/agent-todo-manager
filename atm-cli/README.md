# atm-cli

Command-line interface for the Agent Todo Manager. Provides AI agents with the ability to read and manipulate projects, stories, tasks, steps, and completions.

## Agent roles

The CLI is role-agnostic — any agent can call any command. By convention, two roles are expected:

**PM agent** — responsible for planning and structure:
- Create and delete stories
- Create and delete tasks
- Update story and task status during replanning

**Worker agent** — responsible for execution:
- Claim work by logging a `started` completion
- Progress through steps, updating status as it goes
- Create or delete steps when breaking down or recovering from mistakes
- Log a `completed` completion when done
