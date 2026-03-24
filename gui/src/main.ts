import './style.css';
import { provider } from './api.ts';
import { renderProject } from './render.ts';

const PROJECT_ID = '00000000-0000-0000-0000-000000000001';
const POLL_INTERVAL_MS = 3000;

function renderError(message: string): void {
  const app = document.getElementById('app');
  if (app) {
    app.innerHTML = `<main class="container"><div class="error-state"><p>Error: ${message}</p></div></main>`;
  }
}

async function tick(): Promise<void> {
  try {
    const project = await provider.getProject(PROJECT_ID);
    renderProject(project);
  } catch (err) {
    renderError(err instanceof Error ? err.message : 'Unknown error');
  }
}

void tick();
setInterval(() => {
  void tick();
}, POLL_INTERVAL_MS);
