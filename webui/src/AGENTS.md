# OpenMOSS/webui — Vue 3 Frontend

**Generated:** 2026-03-19

## OVERVIEW

Vue 3 admin dashboard (TypeScript + Tailwind CSS v4 + shadcn-vue + Pinia + vue-router 5). Dev: port 5173 with `/api` proxy to backend :6565. Prod: built to `dist/` → copied to `static/`.

## STRUCTURE

```
webui/src/
├── main.ts              # Vue app bootstrap
├── App.vue              # Root component
├── router/index.ts      # Vue Router 5 (all routes)
├── stores/              # Pinia stores (auth.ts, counter.ts)
├── api/client.ts        # Axios API client
├── composables/         # Composables (useActivityFeed.ts)
├── views/               # 12 page views (TasksView, DashboardView, etc.)
└── components/
    ├── ui/              # shadcn-vue components (table, button, card, sidebar, etc.)
    ├── feed/            # Feed-specific components
    └── common/          # Shared components
```

## WHERE TO LOOK

| Need | Location |
|------|----------|
| Add new page | `views/NewPage.vue` + register in `router/index.ts` |
| API call | `api/client.ts` — add method, use in views |
| State management | `stores/` (Pinia) |
| UI component | `components/ui/` (shadcn-vue) |
| Route guard | `router/index.ts` — add `beforeEach` or meta |

## CONVENTIONS

- **Path alias**: `@/*` → `./src/` (tsconfig + vite configured).
- **No semicolons**, single quotes, 100-char max line width (Prettier).
- **Single-word components allowed**: Avatar, Badge, etc. (`'vue/multi-word-component-names': 'off'`).
- **`@typescript-eslint/no-explicit-any`**: Warn level (not error).
- **UI components**: shadcn-vue style — barrel exports from `index.ts` in each component dir.
- **Tailwind v4**: CSS-first config via `@theme` in CSS, not `tailwind.config.js`.
- **`noUncheckedIndexedAccess`**: true in tsconfig — array access returns `T | undefined`.
- **Router mode**: History mode (HTML5 pushState), SPA catch-all handled by backend.
- **Proxy**: Vite dev proxies `/api` → `http://localhost:6565`.

## ANTI-PATTERNS

- ⚠️ **DO NOT** commit `node_modules/` or `dist/` — both are gitignored.
- ⚠️ **DO NOT** use class-based Tailwind — use CSS variables from `@theme` block.
- ⚠️ **DO NOT** hardcode API URLs — use `VITE_*` env vars or `api/client.ts` base URL.

## LINTING

```bash
npm run lint      # oxlint + eslint (both with --fix)
npm run format    # prettier --write
npm run type-check  # vue-tsc --build
```

## KEY ROUTES

| Path | View | Auth |
|------|------|------|
| `/setup` | SetupView | None (blocked post-init) |
| `/login` | LoginView | None |
| `/dashboard` | DashboardView | Admin |
| `/tasks` | TasksView | Admin |
| `/agents` | AgentsView | Admin |
| `/feed` | FeedView | Admin (or public if `public_feed: true`) |
| `/scores` | ScoresView | Admin |
| `/reviews` | ReviewsView | Admin |
| `/logs` | LogsView | Admin |
| `/prompts` | PromptsView | Admin |
| `/settings` | SettingsView | Admin |

## STACK

Vue 3.5 | vue-router 5 | Pinia 3 | Tailwind CSS v4 | shadcn-vue | reka-ui | axios | vueuse | marked | vue-sonner
