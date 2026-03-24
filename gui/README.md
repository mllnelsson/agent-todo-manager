# gui

Read-only observability dashboard. Vanilla TypeScript + Vite + Pico CSS.

## Role

Renders current project state — stories, tasks, steps, and activity feed. No business logic, no writes, no user input.

The API does not exist yet. Data is loaded from `examples/sample_project.json` via a swappable `DataProvider` abstraction.

## Stack

- **Vite** — dev server and bundler
- **Vanilla TypeScript** — no framework
- **Pico CSS** — classless base styles via CDN

## File Structure

```
gui/
├── index.html
├── vite.config.ts         # Dev proxy: /api → localhost:8000
├── tsconfig.json
├── package.json
├── examples/
│   └── sample_project.json   # Static fixture used during development
└── src/
    ├── main.ts        # Entry point. Polling loop (3s interval).
    ├── api.ts         # DataProvider interface + StaticProvider (reads JSON fixture).
    ├── render.ts      # DOM rendering. Called by main on each poll.
    ├── style.css      # Project-specific overrides on top of Pico CSS.
    └── types.ts       # TypeScript interfaces for Project, Story, Task, Step, Completion.
```

## Behavior

- Polls the data provider every 3 seconds via `setInterval`
- On each tick: fetch project → replace `#app` contents
- On error: shows error state; polling continues

## Swapping to the real API

When the FastAPI backend is ready, open `src/api.ts` and replace:

```ts
export const provider: DataProvider = new StaticProvider();
```

with an `ApiProvider` that calls `fetch('/api/projects/{id}')` implementing the same `DataProvider` interface. No other files need to change.

## Dev

```sh
npm run dev      # starts at http://localhost:5173
npm run build    # type-check + bundle
```

## Constraints

- No interactive prompts or forms
- No writes to the backend
- `types.ts` must stay in sync with the Pydantic response models from `api`
