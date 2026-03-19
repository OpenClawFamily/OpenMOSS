# OpenMOSS/prompts — Agent Role Prompts

**Generated:** 2026-03-19

## OVERVIEW

Structured prompts for 4 agent roles. Prompts define WHAT each agent SHOULD DO (behavior/goals), as opposed to Skills which define HOW (tools/capabilities).

## STRUCTURE

```
prompts/
├── agents/       # Agent-specific prompt overrides
├── role/         # Role-specific prompts (task-planner, task-executor, task-reviewer, task-patrol)
├── templates/    # Task templates (used by Planner to create sub-tasks)
└── tool/         # Tool prompt fragments
```

## WHERE TO LOOK

| Need | Location |
|------|----------|
| Planner behavior | `role/task-planner.md` or `agents/task-planner.md` |
| Executor behavior | `role/task-executor.md` or `agents/task-executor.md` |
| Reviewer behavior | `role/task-reviewer.md` or `agents/task-reviewer.md` |
| Patrol behavior | `role/task-patrol.md` or `agents/task-patrol.md` |
| Task templates | `templates/` (Markdown outlines for sub-task creation) |

## KEY DISTINCTION

- **Prompts (`prompts/`)**: Define agent goals, behavior, workflow — the "soul" of each role.
- **Skills (`skills/`)**: Define agent capabilities/tools — the "hands" that execute.

Both are served to agents at runtime via OpenMOSS API (`/agents/me/prompt`, `/agents/me/skill`).

## NOTES

- Prompts can be viewed and edited via WebUI at `/prompts`.
- Global rules in `rules/global-rule-example.md` are injected into all agent prompts.
- Task templates in `templates/` are referenced by Planner when breaking down tasks into sub-tasks.
