import type { Status } from './types.ts';

export type TabId = 'projects' | 'agents';

export function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function badge(status: Status): string {
  const label: Record<Status, string> = {
    todo: 'TODO',
    in_progress: 'IN PROGRESS',
    completed: 'COMPLETED',
  };
  const cls = status.replace('_', '-');
  return `<span class="badge badge--${cls}">${label[status]}</span>`;
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function buildTabBar(activeTab: TabId): string {
  const tabs: { id: TabId; label: string }[] = [
    { id: 'projects', label: 'Projects' },
    { id: 'agents',   label: 'Agents' },
  ];
  const buttons = tabs
    .map(({ id, label }) => {
      const active = id === activeTab ? ' tab-btn--active' : '';
      return `<button class="tab-btn${active}" data-tab="${id}">${label}</button>`;
    })
    .join('');
  return `<nav class="tab-bar">${buttons}</nav>`;
}
