# gui

Read-only observability dashboard. Vanilla TypeScript + Vite.

## Role

Renders live project state — stories, tasks, steps, bugs, hotfixes, and activity feed. Two views:

- **Projects tab** — sidebar lists all projects; selecting one shows its full detail
- **Agents tab** — shows all in-progress tasks across all projects, grouped by the agent working on each

No business logic, no writes, no user input. Polls the API every 3 seconds.

## Stack

- **Vite** — dev server and bundler
- **Vanilla TypeScript** — no framework

## Setup

**Prerequisites:** Node.js 18+

```sh
cd gui
npm install
```

## Running

The dev server proxies `/api` requests to `http://localhost:8000`, so the API must be running first.

```sh
npm run dev      # starts at http://localhost:5173
npm run build    # type-check + bundle
npm test         # unit tests (vitest)
```

## File Structure

```
gui/
├── index.html
├── vite.config.ts          # Dev proxy: /api → localhost:8000
├── tsconfig.json
├── vitest.config.ts
├── package.json
└── src/
    ├── main.ts             # Entry point. Tab + project selection state. Polling loop (3s).
    ├── api.ts              # DataProvider interface + HTTPProvider.
    ├── render-utils.ts     # Shared primitives: TabId, escapeHtml, badge, formatDate, buildTabBar.
    ├── render-project.ts   # Project/story/task/step builders, activity feed, renderProject/Tab.
    ├── render-agents.ts    # Agent task collection, agent view, renderAgentTab.
    ├── style.css           # Dark theme styles.
    └── types.ts            # TypeScript interfaces: Project, Story, Task, Step, Completion.
```

## Behavior

- On each tick: fetches all projects via `GET /api/projects`, then renders the active tab
- **Projects tab:** auto-selects the first project; clicking a sidebar item switches the detail view
- **Agents tab:** scans all in-progress tasks across all projects and resolves the responsible agent from the latest `started` completion for each task
- On error: shows error state; polling continues

## Constraints

- No interactive prompts or forms
- No writes to the backend
- `types.ts` must stay in sync with the Pydantic response models from `api`
