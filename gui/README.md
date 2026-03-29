# gui

Read-only observability dashboard. Vanilla TypeScript + Vite + Pico CSS.

## Role

Renders current project state — stories, tasks, steps, and activity feed. No business logic, no writes, no user input.

Polls the API every 3 seconds. Requires the `api` service to be running.

## Stack

- **Vite** — dev server and bundler
- **Vanilla TypeScript** — no framework
- **Pico CSS** — classless base styles via CDN

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
```

```sh
npm run build    # type-check + bundle
```

## File Structure

```
gui/
├── index.html
├── vite.config.ts         # Dev proxy: /api → localhost:8000
├── tsconfig.json
├── package.json
└── src/
    ├── main.ts        # Entry point. Polling loop (3s interval).
    ├── api.ts         # DataProvider interface + HTTPProvider.
    ├── render.ts      # DOM rendering. Called by main on each poll.
    ├── style.css      # Project-specific overrides on top of Pico CSS.
    └── types.ts       # TypeScript interfaces for Project, Story, Task, Step, Completion.
```

## Behavior

- Polls the API every 3 seconds via `setInterval`
- On each tick: fetch project → replace `#app` contents
- On error: shows error state; polling continues

## Constraints

- No interactive prompts or forms
- No writes to the backend
- `types.ts` must stay in sync with the Pydantic response models from `api`
