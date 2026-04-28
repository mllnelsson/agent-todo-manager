import type { Completion, Project, Step, Story, Task } from './types.ts';
import { badge, buildTabBar, escapeHtml, formatDate } from './render-utils.ts';
import type { TabId } from './render-utils.ts';

function buildEntityIndex(project: Project): Map<string, string> {
  const index = new Map<string, string>();
  for (const story of project.stories) {
    index.set(story.id, `story ${story.seq}`);
    for (const task of story.tasks) {
      index.set(task.id, `task ${story.seq}.${task.seq}`);
      for (const step of task.steps) {
        index.set(step.id, `step ${story.seq}.${task.seq}.${step.seq}`);
      }
    }
  }
  for (const task of project.bugs) {
    index.set(task.id, `bug b.${task.seq}`);
    for (const step of task.steps) {
      index.set(step.id, `step b.${task.seq}.${step.seq}`);
    }
  }
  for (const task of project.hotfixes) {
    index.set(task.id, `hotfix h.${task.seq}`);
    for (const step of task.steps) {
      index.set(step.id, `step h.${task.seq}.${step.seq}`);
    }
  }
  return index;
}

export function buildStep(step: Step, address: string): string {
  return `
    <div class="step">
      <span class="address">${escapeHtml(address)}</span>
      <span class="step-title">${escapeHtml(step.title)}</span>
    </div>`;
}

function buildTask(task: Task, address: string): string {
  const steps = task.steps
    .map((s) => buildStep(s, `${address}.${s.seq}`))
    .join('');
  return `
    <div class="task" data-status="${task.status}">
      <div class="task-header">
        <span class="address">${escapeHtml(address)}</span>
        <span class="task-title">${escapeHtml(task.title)}</span>
        ${badge(task.status)}
      </div>
      <p class="task-description">${escapeHtml(task.description)}</p>
      <div class="step-list">${steps}</div>
    </div>`;
}

function buildStory(story: Story): string {
  const tasks = story.tasks
    .map((t) => buildTask(t, `${story.seq}.${t.seq}`))
    .join('');
  return `
    <article class="story" data-status="${story.status}">
      <div class="story-header">
        <span class="address">${story.seq}</span>
        <h3>${escapeHtml(story.title)}</h3>
        ${badge(story.status)}
      </div>
      <p class="story-description">${escapeHtml(story.description)}</p>
      <div class="task-list">
        ${tasks || '<p class="empty-state">No tasks yet.</p>'}
      </div>
    </article>`;
}

function buildFloatingTaskGroup(tasks: Task[], prefix: string, label: string): string {
  if (tasks.length === 0) {
    return `
      <div class="floating-group">
        <h3>${label}</h3>
        <p class="empty-state">None.</p>
      </div>`;
  }
  const items = tasks
    .map((t) => buildTask(t, `${prefix}.${t.seq}`))
    .join('');
  return `
    <div class="floating-group">
      <h3>${label}</h3>
      ${items}
    </div>`;
}

function buildActivityFeed(completions: Completion[], entityIndex: Map<string, string>): string {
  if (completions.length === 0) {
    return '<p class="empty-state">No activity yet.</p>';
  }

  const sorted = [...completions].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  const rows = sorted
    .map((c) => {
      const entity = entityIndex.get(c.entity_id) ?? `${c.entity_type} ${c.entity_id.slice(0, 8)}…`;
      const branch = c.branch ? escapeHtml(c.branch) : '—';
      return `
        <div class="activity-row">
          <span class="activity-time">${formatDate(c.created_at)}</span>
          <span class="activity-agent">${escapeHtml(c.agent_name)}</span>
          <span class="activity-action activity-action--${c.action}">${c.action}</span>
          <span class="activity-entity">${escapeHtml(entity)}</span>
          <span class="activity-branch">${branch}</span>
        </div>`;
    })
    .join('');

  return `
    <div class="activity-feed">
      <span class="activity-header">Time</span>
      <span class="activity-header">Agent</span>
      <span class="activity-header">Action</span>
      <span class="activity-header">Entity</span>
      <span class="activity-header">Branch</span>
      ${rows}
    </div>`;
}

function buildProjectDetail(project: Project): string {
  const entityIndex = buildEntityIndex(project);
  const hasFloating = project.bugs.length > 0 || project.hotfixes.length > 0;
  const storiesHtml = project.stories.map(buildStory).join('');

  const floatingHtml = hasFloating
    ? `
      <section class="floating-tasks-section">
        <h2>Bugs &amp; Hotfixes</h2>
        <div class="floating-columns">
          ${buildFloatingTaskGroup(project.bugs, 'b', 'Bugs')}
          ${buildFloatingTaskGroup(project.hotfixes, 'h', 'Hotfixes')}
        </div>
      </section>`
    : '';

  return `
    <header class="project-header">
      <div class="project-title">
        <h1>${escapeHtml(project.title)}</h1>
        ${badge(project.status)}
      </div>
      <p>${escapeHtml(project.description)}</p>
      <div class="project-meta">
        <span>Updated: ${formatDate(project.updated_at)}</span>
      </div>
    </header>

    <section class="stories-section">
      <h2>Stories</h2>
      ${storiesHtml || '<p class="empty-state">No stories yet.</p>'}
    </section>

    ${floatingHtml}

    <section class="activity-section">
      <h2>Activity</h2>
      ${buildActivityFeed(project.completions, entityIndex)}
    </section>`;
}

export function renderProjectTab(projects: Project[], selected: Project | null, activeTab: TabId): void {
  const app = document.getElementById('app');
  if (!app) return;

  const navItems = projects
    .map((p) => {
      const active = p.id === selected?.id ? ' project-nav-item--active' : '';
      return `
        <button class="project-nav-item${active}" data-project-id="${p.id}">
          <span class="project-nav-title">${escapeHtml(p.title)}</span>
          ${badge(p.status)}
        </button>`;
    })
    .join('');

  const detailHtml = selected
    ? buildProjectDetail(selected)
    : '<p class="empty-state">Select a project.</p>';

  app.innerHTML = `
    ${buildTabBar(activeTab)}
    <div class="project-layout">
      <aside class="project-sidebar">
        <div class="project-sidebar-label">// PROJECTS</div>
        ${navItems || '<p class="empty-state">No projects.</p>'}
      </aside>
      <main class="project-main">
        ${detailHtml}
      </main>
    </div>`;
}

export function renderProject(project: Project): void {
  const app = document.getElementById('app');
  if (!app) return;

  app.innerHTML = `<main class="container">${buildProjectDetail(project)}</main>`;
}
