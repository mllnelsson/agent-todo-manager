import type { Completion, Project, Task } from './types.ts';
import { badge, buildTabBar, escapeHtml } from './render-utils.ts';
import type { TabId } from './render-utils.ts';
import { buildStep } from './render-project.ts';

interface ActiveTaskEntry {
  task: Task;
  address: string;
  projectTitle: string;
  context: string;
}

function collectActiveTasks(projects: Project[]): Map<string, ActiveTaskEntry[]> {
  const agentMap = new Map<string, ActiveTaskEntry[]>();

  function findAgent(taskId: string, completions: Completion[]): string {
    const latest = completions
      .filter((c) => c.entity_id === taskId && c.action === 'started')
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
    return latest?.agent_name ?? 'unknown';
  }

  function addEntry(agent: string, entry: ActiveTaskEntry): void {
    if (!agentMap.has(agent)) agentMap.set(agent, []);
    agentMap.get(agent)!.push(entry);
  }

  for (const project of projects) {
    for (const story of project.stories) {
      for (const task of story.tasks) {
        if (task.status === 'in_progress') {
          addEntry(findAgent(task.id, project.completions), {
            task,
            address: `${story.seq}.${task.seq}`,
            projectTitle: project.title,
            context: story.title,
          });
        }
      }
    }
    for (const task of project.bugs) {
      if (task.status === 'in_progress') {
        addEntry(findAgent(task.id, project.completions), {
          task,
          address: `b.${task.seq}`,
          projectTitle: project.title,
          context: 'Bugs',
        });
      }
    }
    for (const task of project.hotfixes) {
      if (task.status === 'in_progress') {
        addEntry(findAgent(task.id, project.completions), {
          task,
          address: `h.${task.seq}`,
          projectTitle: project.title,
          context: 'Hotfixes',
        });
      }
    }
  }

  return agentMap;
}

function buildAgentView(projects: Project[]): string {
  const agentMap = collectActiveTasks(projects);

  if (agentMap.size === 0) {
    return '<p class="empty-state">No active agents.</p>';
  }

  const cards = [...agentMap.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([agent, entries]) => {
      const taskCount = entries.length;
      const taskItems = entries
        .map(({ task, address, projectTitle, context }) => {
          const stepList = task.steps
            .map((s) => buildStep(s, `${address}.${s.seq}`))
            .join('');
          return `
            <div class="task" data-status="${task.status}">
              <div class="task-header">
                <span class="address">${escapeHtml(address)}</span>
                <span class="task-title">${escapeHtml(task.title)}</span>
                ${badge(task.status)}
              </div>
              <p class="agent-task-context">${escapeHtml(projectTitle)} › ${escapeHtml(context)}</p>
              ${stepList ? `<div class="step-list">${stepList}</div>` : ''}
            </div>`;
        })
        .join('');
      return `
        <article class="agent-card">
          <div class="agent-card-header">
            <span class="agent-card-name">${escapeHtml(agent)}</span>
            <span class="agent-card-count">${taskCount} active task${taskCount === 1 ? '' : 's'}</span>
          </div>
          <div class="agent-card-tasks">${taskItems}</div>
        </article>`;
    })
    .join('');

  return `<div class="agent-list">${cards}</div>`;
}

export function renderAgentTab(projects: Project[], activeTab: TabId): void {
  const app = document.getElementById('app');
  if (!app) return;

  app.innerHTML = `
    ${buildTabBar(activeTab)}
    <main class="container">
      <section class="agent-section">
        <h2>Active Agents</h2>
        ${buildAgentView(projects)}
      </section>
    </main>`;
}
