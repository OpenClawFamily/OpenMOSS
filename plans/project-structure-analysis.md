# OpenMOSS 项目结构分析与重构计划

## 一、项目概述

OpenMOSS 是一个基于 OpenClaw 的自组织多 Agent 协作平台，采用中间件架构。

### 设计文档定义的结构

根据 README.md，项目的设计结构如下：

| 层次 | 描述 |
|------|------|
| Frontend | Vue 3 + shadcn-vue 管理后台 |
| Backend | FastAPI (:6565) RESTful API |
| Database | SQLite + SQLAlchemy (10 张表) |
| Agent Runtime | OpenClaw (每个 Agent 是带有 Role Prompt + Skill 的实例) |

### 任务层级

| 层级 | 描述 |
|------|------|
| Task | 完整项目目标 |
| Module | 任务的功能分解 |
| Sub-Task | 可执行的最小工作单元 |

---

## 二、当前目录结构分析

### 2.1 整体结构

```
h:/project/OpenMOSS/
├── app/                    # ✅ FastAPI 后端代码
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth/               # 认证模块
│   ├── middleware/         # 中间件
│   ├── models/             # SQLAlchemy 模型
│   ├── routers/            # API 路由
│   ├── schemas/            # Pydantic schemas
│   └── services/           # 业务逻辑
├── skills/                 # ⚠️ 与 OpenMOSS/skills 重复
├── prompts/                # ⚠️ 与 OpenMOSS/prompts 部分重复
├── rules/                  # ✅ 全局规则
├── docs/                  # ✅ 部署文档
├── static/                # ✅ 前端静态资源
├── webui/                 # ✅ Vue 源代码
├── OpenMOSS/              # ⚠️ 疑似重复目录
│   ├── app/               # ❌ 重复的后端代码？
│   ├── skills/            # ⚠️ 与根目录 skills/ 重复
│   ├── prompts/           # ⚠️ 与根目录 prompts/ 重复
│   ├── docs/              # ⚠️ 与根目录 docs/ 重复
│   ├── static/
│   ├── webui/
│   ├── workspace/         # 工作区文件
│   └── ...
├── plans/                 # ✅ 计划文档
├── config.yaml            # 运行时配置
├── config.example.yaml    # 配置模板
├── requirements.txt       # Python 依赖
└── README*.md             # 项目文档
```

### 2.2 重复目录详细对比

| 目录 | 根目录 | OpenMOSS/ | 差异分析 |
|------|--------|-----------|----------|
| `skills/` | ✅ 存在 | ✅ 存在 | 根目录缺少 `novel-writing/`, `novel-writing-skill/` |
| `prompts/` | ✅ 存在 | ✅ 存在 | 根目录缺少 4 个 executor 文件 |
| `docs/` | ✅ 存在 | ✅ 存在 | 需要对比内容是否一致 |
| `app/` | ✅ 核心代码 | ⚠️ 可能存在 | 需要确认 |

---

## 三、问题识别

### 3.1 高优先级问题

| # | 问题 | 影响 | 建议 |
|---|------|------|------|
| 1 | **目录重复** | 维护困难，可能导致文件版本不一致 | 合并或明确分工 |
| 2 | **OpenMOSS/app/ 是否需要** | 如果是同一套代码则冗余 | 确认是否存在并清理 |
| 3 | **配置文件位置** | config.yaml 在根目录，不在 app/ | 建议移入 app/config/ |

### 3.2 中等优先级问题

| # | 问题 | 建议 |
|---|------|------|
| 4 | `prompts/role/backend-developer-executor.md` 等 4 个文件只在 OpenMOSS/prompts/role/ 中存在 | 需要同步到根目录 prompts/role/ |
| 5 | novel-writing 相关 skill 只在 OpenMOSS/skills/ 中存在 | 确认是否需要 |
| 6 | static/ 和 webui/ 的关系 | static 是构建产物，webui 是源码，建议在 .gitignore 中排除 static |

### 3.3 低优先级问题（代码规范）

| # | 问题 | 建议 |
|---|------|------|
| 7 | app/routers/ 有 16 个文件，可能过大 | 考虑按功能模块拆分 |
| 8 | app/services/ 有 15 个文件，查询服务和业务逻辑混合 | 考虑分离 |
| 9 | 缺少统一的异常处理模块 | 可抽取到 middleware/ |

---

## 四、重构方案

### 4.1 方案一：清理重复目录（推荐）

**目标**：统一目录结构，消除重复

```
h:/project/OpenMOSS/
├── app/                    # 保留
├── skills/                 # 保留（合并后的完整版本）
├── prompts/                # 保留（合并后的完整版本）
├── rules/                  # 保留
├── docs/                   # 保留
├── static/                 # 保留（构建产物）
├── webui/                  # 保留（源码）
├── plans/                  # 保留
├── config.yaml             # 保留
├── requirements.txt        # 保留
└── README*.md              # 保留

# 删除以下重复内容
├── OpenMOSS/               # ⚠️ 整个目录可能需要删除或重构
```

**操作步骤**：
1. 检查 OpenMOSS/ 目录是否被 git submodule 引用
2. 确认 OpenMOSS/app/ 内容是否与根 app/ 相同
3. 将 OpenMOSS/skills/ 中独有的内容（novel-writing等）复制到根 skills/
4. 将 OpenMOSS/prompts/ 中独有的内容复制到根 prompts/
5. 删除 OpenMOSS/ 目录或将其转换为输出目录

### 4.2 方案二：保留双目录结构

如果 OpenMOSS/ 是作为"示例输出"或"子项目"存在：

```
h:/project/OpenMOSS/
├── app/                    # 主项目后端
├── skills/                 # 主项目 skills
├── prompts/                # 主项目 prompts
├── ...
└── OpenMOSS/              # 作为示例/输出目录保留
    ├── skills/             # 示例 skills（供用户参考）
    ├── prompts/           # 示例 prompts
    ├── workspace/         # AI 工作输出
    └── openmoss-outputs/  # AI 交付物
```

**需要**：
- 在 OpenMOSS/ 添加 README 说明其用途
- 在 .gitignore 中排除 OpenMOSS/workspace/

---

## 五、待确认问题

在执行重构前，需要确认：

1. **OpenMOSS/ 目录的用途是什么？**
   - 是历史遗留的重复代码？
   - 还是作为示例/输出目录？

2. **配置文件应该放在哪里？**
   - 当前：根目录 config.yaml
   - 建议：app/config/

3. **是否需要 novel-writing 相关 skill？**
   - 如果不需要，可以从 OpenMOSS/skills/ 删除

4. **static/ 目录是否应该提交到 git？**
   - 建议：在 .gitignore 中排除，构建时生成

---

## 六、行动计划

### 立即执行（低风险）
- [ ] 1. 在 .gitignore 中排除 `static/` 构建产物
- [ ] 2. 同步 prompts/role/ 中缺少的 4 个文件

### 谨慎执行（需要备份）
- [ ] 3. 备份并检查 OpenMOSS/ 目录内容
- [ ] 4. 确认 app/ 和 OpenMOSS/app/ 的关系
- [ ] 5. 决定是否删除 OpenMOSS/ 目录或其中的重复内容

### 长期改进
- [ ] 6. 拆分 app/routers/ 为更小的模块
- [ ] 7. 抽取统一异常处理
- [ ] 8. 添加更多单元测试

---

*生成时间：2026-03-13*
