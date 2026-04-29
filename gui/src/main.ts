import './style.css';
import { provider } from './api.ts';
import type { TabId } from './render-utils.ts';
import { renderProjectTab } from './render-project.ts';
import { renderAgentTab } from './render-agents.ts';

const POLL_INTERVAL_MS = 3000;

let activeTab: TabId = 'projects';
let selectedProjectId: string | null = null;
const expandedStoryIds = new Set<string>();
const manuallyToggled = new Set<string>();

function renderError(message: string): void {
  const app = document.getElementById('app');
  if (app) {
    app.innerHTML = `<main class="container"><div class="error-state"><p>Error: ${message}</p></div></main>`;
  }
}

async function tick(): Promise<void> {
  try {
    const projects = await provider.listProjects();
    if (selectedProjectId === null && projects.length > 0) {
      selectedProjectId = projects[0].id;
    }
    if (activeTab === 'projects') {
      const selected = selectedProjectId ? await provider.getProject(selectedProjectId) : null;
      if (selected) {
        for (const story of selected.stories) {
          if (story.status === 'in_progress' && !manuallyToggled.has(story.id)) {
            expandedStoryIds.add(story.id);
          }
        }
      }
      renderProjectTab(projects, selected, activeTab, expandedStoryIds);
    } else {
      const fullProjects = await Promise.all(projects.map((p) => provider.getProject(p.id)));
      renderAgentTab(fullProjects, activeTab);
    }
  } catch (err) {
    renderError(err instanceof Error ? err.message : 'Unknown error');
  }
}

document.addEventListener('click', (e) => {
  const target = e.target as HTMLElement;

  const tabBtn = target.closest<HTMLElement>('[data-tab]');
  if (tabBtn?.dataset['tab']) {
    const newTab = tabBtn.dataset['tab'] as TabId;
    if (newTab !== activeTab) {
      activeTab = newTab;
      void tick();
    }
    return;
  }

  const storyHeader = target.closest<HTMLElement>('[data-story-toggle]');
  if (storyHeader?.dataset['storyToggle']) {
    const storyId = storyHeader.dataset['storyToggle'];
    manuallyToggled.add(storyId);
    if (expandedStoryIds.has(storyId)) {
      expandedStoryIds.delete(storyId);
    } else {
      expandedStoryIds.add(storyId);
    }
    void tick();
    return;
  }

  const projectBtn = target.closest<HTMLElement>('[data-project-id]');
  if (projectBtn?.dataset['projectId']) {
    const newId = projectBtn.dataset['projectId'];
    if (newId !== selectedProjectId) {
      selectedProjectId = newId ?? null;
      void tick();
    }
  }
});

void tick();
setInterval(() => {
  void tick();
}, POLL_INTERVAL_MS);
