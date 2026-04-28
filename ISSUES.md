# ISSUES

## Reported 2025-04-28
### 1. Smart progress and comepltion ✅ Completed (2026-04-28)
We previously had an issue detailing this reqeust:

```markdown
The agent seemed to struggle in completeing and starting stories, instead focusing on the tasks. We could make so that when we do task start we check if this is the first task in the story, if so and the story is not started we mark that as in progress as well. We do the smae thing when comeplteing a task, if all tasks are ceompleted we comepltete the whole story automatically
```
A fix was made but after testing this out today i still did not experience the behaviour. I think we should enforce this smart behaviour. Everytime a task status is touched we should assert the state of the story and change if it is incostistent. This might relate to issue number 3.

### 2. Ability to clean up tasks
There is right now no possibility in the ordinary (none admin) cli to clean up tasks, some time the planning agent mmesses up and then the atm gets in an akward state with lots of incomplete tasks. Functionality to remove / update tasks and steps should be added to the CLI, and properyl docuemtned in the reference and bundled skill.

### 3. Status on step shouild be removed ✅ Completed (2026-04-28)
Even thoug the project tracks in a x.y.z manner the step is in practise not the best unit of work that can be tracked with a todo -> in progress -> completed status. The agent implmenting seem to mess this upp all the time. I am thinking we should remove the status from step al together. This makes it easier to handle. The steps then mainly serve the purpose of the planning agent to help the builder agent what sequence to do things, offloading this from the building agent. This change must be documented properly in reference and bundled skill.

### 4. Expanding stories in gui.
Right now the project view for a project with multiple stories and multiple task introduces a. lot. of. scrolling.... I want to have a expander function to the proejct view. Each story is un-expanded unless it is in progress.

### 5. Project status
Projct status is right now tricky. I want to change it to be a binary value. Active (default-no visual confirmation its there) or Archived. Archived projects can be viewed but not modified in anyway. We should show both in the gui but in the project picker we should highlight which projects are archived. The admin cli will be the point of entry for changing the sattus of  a proejct.
