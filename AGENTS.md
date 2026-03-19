# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-19
**Project:** OpenMOSS — Self-Organizing Multi-Agent System for OpenClaw

## OVERVIEW

Dual-stack middleware: Python/FastAPI backend orchestrates AI agents via REST API; Vue 3/Tailwind frontend serves as admin dashboard. Agents (planner/executor/reviewer/patrol) collaborate autonomously through cron-wakeup on OpenClaw runtime.

## STRUCTURE

```
OpenMOSS/                     ← ROOT (monorepo)
├── app/                      # FastAPI backend (port 6565)
├── webui/                    # Vue 3 frontend (Vite dev:5173)
├── static/                   # Built frontend (served by backend)
├── skills/                   # OpenClaw agent skill packages
├── prompts/                  # Role prompts (agents/role/templates/tool/)
├── rules/                    # Global rule templates
├── docs/                     # Deployment guides
├── data/                     # SQLite DB + workspace
├── plans/                    # Project plans
└── OpenMOSS/                # ⚠️ Duplicate copy (ignore, not active)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Backend API dev | `OpenMOSS/app/` | FastAPI routers, services, models |
| Frontend dev | `OpenMOSS/webui/src/` | Vue 3 views, components, stores |
| Agent prompts | `OpenMOSS/prompts/` | 4 role prompts (planner/executor/reviewer/patrol) |
| Agent skills | `OpenMOSS/skills/` | CLI tool + 8 skill packages |
| Config | `config.yaml` / `config.example.yaml` | Admin password, token, workspace root |

## CODE MAP (Key Symbols)

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `app` | FastAPI | `OpenMOSS/app/main.py` | Entry point, route registration, SPA serving |
| `config` | Singleton | `OpenMOSS/app/config.py` | YAML config loader |
| `init_db` | Function | `OpenMOSS/app/database.py` | SQLAlchemy table creation |
| `get_current_agent` | Dependency | `OpenMOSS/app/auth/dependencies.py` | API key auth |

## CONVENTIONS

- **Python**: Standard PEP8, no formatter configured. Chinese comments throughout backend.
- **TypeScript/Vue**: Flat config ESLint + Prettier (no semicolons, single quotes, 100-char width).
- **Component naming**: Single-word Vue components allowed (Avatar, Badge, etc.).
- **`@/` path alias**: Maps to `webui/src/`.
- **No `src/` for Python**: Backend lives directly in `app/`, not `app/src/`.
- **API prefix**: All routes under `/api`. Module-path import: `from app.routers import agents`.
- **Entry command**: `python -m uvicorn app.main:app` (must run from project root, one level above `app/`).

## ANTI-PATTERNS (THIS PROJECT)

- ⚠️ **DO NOT** run `python app/main.py` directly — import resolution fails. Use module path.
- ⚠️ **DO NOT** write to `AGENTS.md`/`SOUL.md` from platform setup guide (per PromptsView.vue restriction).
- ⚠️ **DO NOT** access `/setup` after initialization — router blocks it.
- ⚠️ **First deploy MUST** change: `admin.password`, `agent.registration_token`, `workspace.root`.

## UNIQUE STYLES

- **Dual static serving**: Frontend built to `webui/dist/` → copied to `static/` → FastAPI serves both API + SPA.
- **SPA catch-all**: All unmatched `GET /{path}` returns `index.html` (Vue Router mode).
- **RequestLoggerMiddleware**: Every agent API call is logged to SQLite → drives activity feed.
- **Skill packaging**: `pack-skills.py` bundles role-specific SKILL.md + task-cli.py into `.zip` for agent distribution.
- **Config auto-gen**: `config.yaml` generated from template on first launch; passwords bcrypt-encrypted.
- **No tests directory**: Despite README listing `tests/`, it doesn't exist. No pytest configured.

## COMMANDS

```bash
# Backend (run from project root)
pip install -r OpenMOSS/requirements.txt
python -m uvicorn OpenMOSS.app.main:app --host 0.0.0.0 --port 6565 --reload

# Frontend
cd OpenMOSS/webui && npm install && npm run dev
cd OpenMOSS/webui && npm run build && cp -r dist/* ../static/

# Lint
cd OpenMOSS/webui && npm run lint
```

## NOTES

- `OpenMOSS/` subdirectory is a complete duplicate of the project — likely a workspace artifact. Ignore it; all work happens in root-level dirs.
- 10 SQLAlchemy models in `app/models/`: task, module, sub_task, agent, review_record, score, reward_log, activity_log, request_log, patrol_record, rule.
- Agents communicate **asynchronously** via REST API — never directly.
- Frontend uses shadcn-vue + Tailwind CSS v4 (not v3) + reka-ui + Pinia + vue-router 5.
