# OpenMOSS/skills — OpenClaw Agent Skills

**Generated:** 2026-03-19

## OVERVIEW

8 self-contained skill packages + shared CLI tool. Each skill defines what an agent can DO (tools/capabilities). Packaged into `.zip` via `pack-skills.py` and distributed to OpenClaw agents.

## STRUCTURE

```
skills/
├── task-cli.py              # Shared API client (all agents use this)
├── pack-skills.py           # Packaging script (bundles SKILL.md + task-cli.py → .zip)
├── dist/                    # Output: packaged .zip skill bundles
├── task-planner-skill/      # Planner role skill
├── task-executor-skill/     # Executor role skill
├── task-reviewer-skill/     # Reviewer role skill
├── task-patrol-skill/       # Patrol role skill
├── wordpress-skill/         # ⚙️ WordPress publishing (external service required)
├── antigravity-gemini-image/ # ⚙️ Gemini image gen (external service required)
├── grok-search-runtime/     # ⚙️ Grok web search (external service required)
├── local-web-search/        # Local gateway web search
├── novel-writing-skill/      # Novel writing capability
└── novel-writing/           # Novel writing resources
```

## WHERE TO LOOK

| Need | Location |
|------|----------|
| CLI tool source | `task-cli.py` — API client wrapping OpenMOSS REST API |
| Package script | `pack-skills.py` — reads SKILL.md, bundles with task-cli.py |
| Skill definition | `*-skill/SKILL.md` — markdown prompt defining agent capabilities |
| New skill | Create `*-skill/SKILL.md` + `references/` dir |

## CONVENTIONS

- **Skill structure**: Each skill is a directory containing `SKILL.md` (main definition) + optional `references/`, CLI scripts, config docs.
- **SKILL.md**: Markdown file defining the skill's role, tools, and behavior. `pack-skills.py` reads it and embeds into `.zip`.
- **task-cli.py**: Shared across all agents — provides register, tasks, submit, review, logs, rules, update commands.
- **⚙️ marker**: Skills marked ⚙️ in parent AGENTS.md require external service configuration (API keys, endpoints). Not plug-and-play.
- **CLI update**: `task-cli.py` supports self-update via `update` command (auto-downloads latest from server).

## ANTI-PATTERNS

- ⚠️ **DO NOT** edit skill `.zip` files directly — edit source in `*-skill/` dirs, then re-run `pack-skills.py`.
- ⚠️ **⚙️ skills** require external service setup — don't distribute without configuration.

## SKILL COMMANDS (task-cli.py)

register | tasks | modules | submit | review | logs | rules | prompt | update
