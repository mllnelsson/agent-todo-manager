import { beforeEach, describe, expect, it } from 'vitest';
import { renderProject } from './render.ts';
import type { Completion, Project, Step, Story, Task } from './types.ts';

// --- Factory helpers ---

function makeStep(overrides: Partial<Step> = {}): Step {
  return {
    id: 'step-id-1',
    seq: 1,
    title: 'A step',
    description: 'Step description',
    status: 'todo',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    ...overrides,
  };
}

function makeTask(overrides: Partial<Task> = {}): Task {
  return {
    id: 'task-id-1',
    seq: 1,
    prefix: null,
    title: 'A task',
    description: 'Task description',
    status: 'todo',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    steps: [],
    ...overrides,
  };
}

function makeStory(overrides: Partial<Story> = {}): Story {
  return {
    id: 'story-id-1',
    seq: 1,
    title: 'A story',
    description: 'Story description',
    status: 'todo',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    tasks: [],
    ...overrides,
  };
}

function makeCompletion(overrides: Partial<Completion> = {}): Completion {
  return {
    id: 'completion-id-1',
    entity_type: 'task',
    entity_id: 'task-id-1',
    action: 'completed',
    agent_name: 'agent-1',
    session_id: 'session-1',
    branch: null,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    ...overrides,
  };
}

function makeProject(overrides: Partial<Project> = {}): Project {
  return {
    id: 'project-id-1',
    title: 'My Project',
    description: 'Project description',
    status: 'in_progress',
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
    stories: [],
    bugs: [],
    hotfixes: [],
    completions: [],
    ...overrides,
  };
}

// --- Tests ---

describe('renderProject', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div id="app"></div>';
  });

  it('does nothing when #app element is missing', () => {
    document.body.innerHTML = '';
    expect(() => renderProject(makeProject())).not.toThrow();
  });

  describe('project header', () => {
    it('renders the project title', () => {
      renderProject(makeProject({ title: 'Test Project' }));
      expect(document.querySelector('h1')?.textContent).toBe('Test Project');
    });

    it('renders the project description', () => {
      renderProject(makeProject({ description: 'My description' }));
      expect(document.querySelector('.project-header p')?.textContent).toBe('My description');
    });

    it('renders in_progress status badge', () => {
      renderProject(makeProject({ status: 'in_progress' }));
      const badge = document.querySelector('.badge--in-progress');
      expect(badge).not.toBeNull();
      expect(badge?.textContent).toBe('IN PROGRESS');
    });

    it('renders todo status badge', () => {
      renderProject(makeProject({ status: 'todo' }));
      const badge = document.querySelector('.badge--todo');
      expect(badge).not.toBeNull();
      expect(badge?.textContent).toBe('TODO');
    });

    it('renders completed status badge', () => {
      renderProject(makeProject({ status: 'completed' }));
      const badge = document.querySelector('.badge--completed');
      expect(badge).not.toBeNull();
      expect(badge?.textContent).toBe('COMPLETED');
    });

    it('escapes HTML in project title', () => {
      renderProject(makeProject({ title: '<script>alert("xss")</script>' }));
      expect(document.querySelector('h1')?.textContent).toBe('<script>alert("xss")</script>');
      expect(document.body.innerHTML).toContain('&lt;script&gt;');
    });

    it('escapes HTML special characters in project description', () => {
      renderProject(makeProject({ description: 'A & B > C "quoted"' }));
      expect(document.querySelector('.project-header p')?.textContent).toBe('A & B > C "quoted"');
      // jsdom re-serializes text nodes: & and > are re-escaped, but " is not (safe in text context)
      expect(document.body.innerHTML).toContain('A &amp; B &gt; C');
    });

    it('renders the updated_at date label', () => {
      renderProject(makeProject({ updated_at: '2024-06-15T12:30:00Z' }));
      expect(document.querySelector('.project-meta')?.textContent).toContain('Updated:');
    });
  });

  describe('stories section', () => {
    it('shows empty state when no stories', () => {
      renderProject(makeProject({ stories: [] }));
      expect(document.querySelector('.stories-section')?.textContent).toContain('No stories yet.');
    });

    it('renders a story title', () => {
      renderProject(makeProject({ stories: [makeStory({ title: 'My Story' })] }));
      expect(document.querySelector('.story h3')?.textContent).toBe('My Story');
    });

    it('renders a story description', () => {
      renderProject(makeProject({ stories: [makeStory({ description: 'Story desc' })] }));
      expect(document.querySelector('.story-description')?.textContent).toBe('Story desc');
    });

    it('renders the story sequence number as address', () => {
      renderProject(makeProject({ stories: [makeStory({ seq: 3 })] }));
      expect(document.querySelector('.story-header .address')?.textContent).toBe('3');
    });

    it('renders the story status badge', () => {
      renderProject(makeProject({ stories: [makeStory({ status: 'completed' })] }));
      expect(document.querySelector('.story .badge--completed')).not.toBeNull();
    });

    it('shows empty task state when story has no tasks', () => {
      renderProject(makeProject({ stories: [makeStory({ tasks: [] })] }));
      expect(document.querySelector('.task-list')?.textContent).toContain('No tasks yet.');
    });

    it('renders multiple stories', () => {
      const stories = [
        makeStory({ seq: 1, title: 'Story One' }),
        makeStory({ id: 'story-2', seq: 2, title: 'Story Two' }),
      ];
      renderProject(makeProject({ stories }));
      expect(document.querySelectorAll('.story')).toHaveLength(2);
    });

    it('escapes HTML in story title', () => {
      renderProject(makeProject({ stories: [makeStory({ title: '<b>Bold</b>' })] }));
      expect(document.querySelector('.story h3')?.textContent).toBe('<b>Bold</b>');
      expect(document.body.innerHTML).toContain('&lt;b&gt;');
    });
  });

  describe('task rendering', () => {
    it('renders task title', () => {
      const story = makeStory({ tasks: [makeTask({ title: 'My Task' })] });
      renderProject(makeProject({ stories: [story] }));
      expect(document.querySelector('.task-title')?.textContent).toBe('My Task');
    });

    it('renders task description', () => {
      const story = makeStory({ tasks: [makeTask({ description: 'Task desc' })] });
      renderProject(makeProject({ stories: [story] }));
      expect(document.querySelector('.task-description')?.textContent).toBe('Task desc');
    });

    it('renders task address as story.task seq', () => {
      const task = makeTask({ seq: 2 });
      const story = makeStory({ seq: 1, tasks: [task] });
      renderProject(makeProject({ stories: [story] }));
      expect(document.querySelector('.task-header .address')?.textContent).toBe('1.2');
    });

    it('renders task status badge', () => {
      const story = makeStory({ tasks: [makeTask({ status: 'in_progress' })] });
      renderProject(makeProject({ stories: [story] }));
      expect(document.querySelector('.task .badge--in-progress')).not.toBeNull();
    });

    it('renders steps nested inside a task', () => {
      const step = makeStep({ title: 'My Step', seq: 1 });
      const task = makeTask({ steps: [step] });
      renderProject(makeProject({ stories: [makeStory({ tasks: [task] })] }));
      expect(document.querySelector('.step-title')?.textContent).toBe('My Step');
    });
  });

  describe('step rendering', () => {
    it('renders step title', () => {
      const step = makeStep({ title: 'Do the thing' });
      const task = makeTask({ steps: [step] });
      renderProject(makeProject({ stories: [makeStory({ tasks: [task] })] }));
      expect(document.querySelector('.step-title')?.textContent).toBe('Do the thing');
    });

    it('renders step address as story.task.step seq', () => {
      const step = makeStep({ seq: 3 });
      const task = makeTask({ seq: 2, steps: [step] });
      const story = makeStory({ seq: 1, tasks: [task] });
      renderProject(makeProject({ stories: [story] }));
      expect(document.querySelector('.step .address')?.textContent).toBe('1.2.3');
    });

    it('renders step status badge', () => {
      const step = makeStep({ status: 'completed' });
      const task = makeTask({ steps: [step] });
      renderProject(makeProject({ stories: [makeStory({ tasks: [task] })] }));
      expect(document.querySelector('.step .badge--completed')).not.toBeNull();
    });

    it('escapes HTML in step title', () => {
      const step = makeStep({ title: '<script>' });
      const task = makeTask({ steps: [step] });
      renderProject(makeProject({ stories: [makeStory({ tasks: [task] })] }));
      expect(document.querySelector('.step-title')?.textContent).toBe('<script>');
      expect(document.body.innerHTML).toContain('&lt;script&gt;');
    });
  });

  describe('bugs and hotfixes section', () => {
    it('does not render floating section when bugs and hotfixes are empty', () => {
      renderProject(makeProject({ bugs: [], hotfixes: [] }));
      expect(document.querySelector('.floating-tasks-section')).toBeNull();
    });

    it('renders floating section when bugs exist', () => {
      renderProject(makeProject({ bugs: [makeTask()], hotfixes: [] }));
      expect(document.querySelector('.floating-tasks-section')).not.toBeNull();
    });

    it('renders floating section when hotfixes exist', () => {
      renderProject(makeProject({ bugs: [], hotfixes: [makeTask()] }));
      expect(document.querySelector('.floating-tasks-section')).not.toBeNull();
    });

    it('shows "None." in bugs group when bugs is empty but hotfixes exist', () => {
      renderProject(makeProject({ bugs: [], hotfixes: [makeTask()] }));
      const groups = document.querySelectorAll('.floating-group');
      expect(groups[0]?.textContent).toContain('None.');
    });

    it('shows "None." in hotfixes group when hotfixes is empty but bugs exist', () => {
      renderProject(makeProject({ bugs: [makeTask()], hotfixes: [] }));
      const groups = document.querySelectorAll('.floating-group');
      expect(groups[1]?.textContent).toContain('None.');
    });

    it('renders bug task with "b." address prefix', () => {
      const bug = makeTask({ seq: 1 });
      renderProject(makeProject({ bugs: [bug] }));
      const addresses = Array.from(document.querySelectorAll('.task-header .address')).map(
        (el) => el.textContent,
      );
      expect(addresses).toContain('b.1');
    });

    it('renders hotfix task with "h." address prefix', () => {
      const hotfix = makeTask({ seq: 2 });
      renderProject(makeProject({ hotfixes: [hotfix] }));
      const addresses = Array.from(document.querySelectorAll('.task-header .address')).map(
        (el) => el.textContent,
      );
      expect(addresses).toContain('h.2');
    });
  });

  describe('activity feed', () => {
    it('shows empty state when no completions', () => {
      renderProject(makeProject({ completions: [] }));
      expect(document.querySelector('.activity-section')?.textContent).toContain('No activity yet.');
    });

    it('renders an activity row per completion', () => {
      const completions = [
        makeCompletion({ id: 'c1', created_at: '2024-01-01T10:00:00Z' }),
        makeCompletion({ id: 'c2', created_at: '2024-01-02T10:00:00Z' }),
      ];
      renderProject(makeProject({ completions }));
      expect(document.querySelectorAll('.activity-row')).toHaveLength(2);
    });

    it('sorts activity rows newest first', () => {
      const completions = [
        makeCompletion({ id: 'c1', agent_name: 'agent-old', created_at: '2024-01-01T10:00:00Z' }),
        makeCompletion({ id: 'c2', agent_name: 'agent-new', created_at: '2024-01-03T10:00:00Z' }),
        makeCompletion({ id: 'c3', agent_name: 'agent-mid', created_at: '2024-01-02T10:00:00Z' }),
      ];
      renderProject(makeProject({ completions }));
      const rows = document.querySelectorAll('.activity-agent');
      expect(rows[0]?.textContent).toBe('agent-new');
      expect(rows[1]?.textContent).toBe('agent-mid');
      expect(rows[2]?.textContent).toBe('agent-old');
    });

    it('renders the agent name', () => {
      renderProject(makeProject({ completions: [makeCompletion({ agent_name: 'my-agent' })] }));
      expect(document.querySelector('.activity-agent')?.textContent).toBe('my-agent');
    });

    it('renders the action', () => {
      renderProject(makeProject({ completions: [makeCompletion({ action: 'started' })] }));
      expect(document.querySelector('.activity-action')?.textContent).toBe('started');
    });

    it('resolves story entity id to story address via entity index', () => {
      const storyId = 'story-id-abc';
      const story = makeStory({ id: storyId, seq: 2 });
      const completion = makeCompletion({ entity_id: storyId, entity_type: 'story' });
      renderProject(makeProject({ stories: [story], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('story 2');
    });

    it('resolves task entity id to task address via entity index', () => {
      const taskId = 'task-id-xyz';
      const task = makeTask({ id: taskId, seq: 2 });
      const story = makeStory({ seq: 1, tasks: [task] });
      const completion = makeCompletion({ entity_id: taskId, entity_type: 'task' });
      renderProject(makeProject({ stories: [story], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('task 1.2');
    });

    it('resolves step entity id to step address via entity index', () => {
      const stepId = 'step-id-xyz';
      const step = makeStep({ id: stepId, seq: 3 });
      const task = makeTask({ seq: 2, steps: [step] });
      const story = makeStory({ seq: 1, tasks: [task] });
      const completion = makeCompletion({ entity_id: stepId, entity_type: 'step' });
      renderProject(makeProject({ stories: [story], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('step 1.2.3');
    });

    it('resolves bug step entity id to bug step address via entity index', () => {
      const stepId = 'bug-step-id';
      const step = makeStep({ id: stepId, seq: 2 });
      const bug = makeTask({ id: 'bug-id', seq: 1, steps: [step] });
      const completion = makeCompletion({ entity_id: stepId, entity_type: 'step' });
      renderProject(makeProject({ bugs: [bug], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('step b.1.2');
    });

    it('resolves bug entity id to bug address via entity index', () => {
      const bugId = 'bug-id-abc';
      const bug = makeTask({ id: bugId, seq: 1 });
      const completion = makeCompletion({ entity_id: bugId, entity_type: 'task' });
      renderProject(makeProject({ bugs: [bug], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('bug b.1');
    });

    it('resolves hotfix entity id to hotfix address via entity index', () => {
      const hotfixId = 'hotfix-id-abc';
      const hotfix = makeTask({ id: hotfixId, seq: 2 });
      const completion = makeCompletion({ entity_id: hotfixId, entity_type: 'task' });
      renderProject(makeProject({ hotfixes: [hotfix], completions: [completion] }));
      expect(document.querySelector('.activity-entity')?.textContent).toBe('hotfix h.2');
    });

    it('uses fallback label for unknown entity id', () => {
      const unknownId = 'abcdef1234567890';
      const completion = makeCompletion({ entity_id: unknownId, entity_type: 'task' });
      renderProject(makeProject({ completions: [completion] }));
      const entityText = document.querySelector('.activity-entity')?.textContent ?? '';
      expect(entityText).toContain('task');
      expect(entityText).toContain(unknownId.slice(0, 8));
    });

    it('shows dash when branch is null', () => {
      renderProject(makeProject({ completions: [makeCompletion({ branch: null })] }));
      expect(document.querySelector('.activity-branch')?.textContent).toBe('—');
    });

    it('shows branch name when branch is set', () => {
      renderProject(makeProject({ completions: [makeCompletion({ branch: 'feature/my-branch' })] }));
      expect(document.querySelector('.activity-branch')?.textContent).toBe('feature/my-branch');
    });

    it('escapes HTML in agent name', () => {
      renderProject(makeProject({ completions: [makeCompletion({ agent_name: '<evil>' })] }));
      expect(document.querySelector('.activity-agent')?.textContent).toBe('<evil>');
      expect(document.body.innerHTML).toContain('&lt;evil&gt;');
    });

    it('escapes HTML in branch name', () => {
      renderProject(makeProject({ completions: [makeCompletion({ branch: '<script>' })] }));
      expect(document.querySelector('.activity-branch')?.textContent).toBe('<script>');
      expect(document.body.innerHTML).toContain('&lt;script&gt;');
    });
  });
});
