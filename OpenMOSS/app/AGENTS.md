# OpenMOSS/app — FastAPI Backend

**Generated:** 2026-03-19

## OVERVIEW

FastAPI REST API (port 6565) — task scheduling, agent management, reviews, scoring, activity logging. No `src/` subdirectory; code lives directly here.

## STRUCTURE

```
app/
├── main.py              # Entry: FastAPI app, lifespan, middleware, route registration
├── config.py            # YAML config loader (singleton)
├── database.py          # SQLAlchemy engine + SessionLocal + init_db()
├── auth/
│   └── dependencies.py  # get_current_agent (API key), get_current_admin (token)
├── middleware/
│   └── request_logger.py # RequestLoggerMiddleware (logs every agent API call)
├── models/              # 10 SQLAlchemy models
├── routers/             # 21 router modules (admin_*, agents, tasks, scores, etc.)
├── services/            # 21 service modules (business logic)
└── schemas/             # 6 admin Pydantic schemas
```

## WHERE TO LOOK

| Need | File |
|------|------|
| Add new API endpoint | `routers/` (follow existing pattern) |
| Business logic | `services/` (task_service, agent_service, etc.) |
| Database model | `models/` (SQLAlchemy declarative) |
| Auth for new route | `auth/dependencies.py` — add dependency |
| Config option | `config.py` — add field, update `config.example.yaml` |

## CONVENTIONS

- **Route registration**: `app.include_router(x.router, prefix=API_PREFIX)` in `main.py`.
- **API prefix**: All routes under `/api` — use module import `from app.routers import agents`.
- **Auth**: Agents use `X-Agent-Key` header → `Depends(get_current_agent)`. Admins use `X-Admin-Token` → `Depends(get_current_admin)`.
- **Chinese comments**: Backend code is Chinese-commented throughout.
- **Service layer**: Routers call services; services handle business logic; models are pure SQLAlchemy.
- **Dual admin split**: `admin/` router for legacy combined endpoints + `admin_*/` routers for separated concerns.
- **No async in services**: Service methods are synchronous (sync functions called from sync route handlers). FastAPI runs them in a thread pool by default.
- **Error handling**: `ValueError` → 400 JSON; unhandled `Exception` → 500 with traceback printed, generic message to client.

## ANTI-PATTERNS

- ⚠️ **DO NOT** import `from app import main` — circular dependency. Import `from app.config import config` instead.
- ⚠️ **DO NOT** add new router without registering it in `main.py`.
- ⚠️ **DO NOT** add new model without running `init_db()` or Alembic migration (no Alembic currently — manual schema).

## UNIQUE STYLES

- **Lifespan context manager**: Database init + old log cleanup happen in `lifespan()` asynccontextmanager.
- **CORS allow-all**: `allow_origins=["*"]` — frontend-backend on same origin in production.
- **Static serving**: Backend mounts Vue build output (`static/`) directly — no separate web server.
- **SPA catch-all**: `GET /{full_path:path}` returns `index.html` for Vue Router.
- **Feed retention**: `_cleanup_old_request_logs()` runs on startup, deletes logs older than `config.feed_retention_days`.

## MODELS (10 tables)

task | module | sub_task | agent | review_record | score | reward_log | activity_log | request_log | patrol_record | rule

## SERVICES (21 files)

| | | | |
|---|---|---|---|
| task_service | sub_task_service | agent_service | review_service |
| reward_service | rule_service | prompt_service | github_service |
| ai_service | notification_service | validator | pagination |
| retry_handler | admin_task_query_service | admin_agent_query_service | admin_score_service |
| admin_score_query_service | admin_review_query_service | admin_log_query_service | admin_dashboard_query_service |

## ROUTERS (21 files)

admin | admin_agents | admin_config | admin_dashboard | admin_logs | admin_reviews | admin_scores | admin_tasks | agents | feed | github_integration | logs | prompts | review_records | rules | scores | setup | sub_tasks | tasks | tools
