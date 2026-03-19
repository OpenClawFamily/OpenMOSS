# OpenMOSS 任务流转问题分析

## 问题描述

1. 任务创建后长期停留在 `pending` 状态
2. Agent 认领任务后没有开始执行（卡在 `assigned`）
3. Agent 执行完成后没有提交（卡在 `in_progress`）

## 根本原因分析

### 1. 任务状态机
```
pending → assigned → in_progress → review → done
```

### 2. 发现的问题

| 问题 | 原因 | 修复 |
|------|------|------|
| 任务卡在 assigned | Agent 没有调用 start | claim 后自动 start（已修复源码） |
| 任务卡在 in_progress | Agent 没有调用 submit | 添加超时自动提交功能 |
| Agent 只处理一个任务 | Cron 消息只让处理一个 | 更新 Cron 消息批量处理 |

### 3. 当前任务状态

| 状态 | 数量 |
|------|------|
| pending | 42 |
| in_progress | 0 |
| review | 1 |
| done | 23 |
| cancelled | 7 |

### 4. Cron 配置问题

旧的 Cron 消息告诉 Agent 只处理 **一个** 任务：
> "用 'st claim <id>' 认领**一个**任务"

新的 Cron 消息让 Agent **批量处理**所有 pending 任务。

## 修复记录

### 2026-03-13 修复

1. **claim_sub_task 自动开始** (`app/services/sub_task_service.py`)
   - 原来：pending → assigned（卡住）
   - 现在：pending → assigned → in_progress

2. **超时自动提交** (`app/services/sub_task_service.py`)
   - 添加 `auto_submit_timeout_tasks` 函数
   - 添加 `/api/sub-tasks/auto-timeout` 端点
   - Patrol Agent 定期调用

3. **批量处理任务** (`cron/jobs.json`)
   - 更新 executor cron 消息
   - 让 Agent 处理所有 pending 任务

4. **GitHub Token 存数据库** (`app/config.py`)
   - 创建 `settings` 表
   - Token 存数据库，不推送到 GitHub

5. **前端 Switch 绑定修复** (`webui/src/views/SettingsView.vue`)
   - 修复 `v-model:checked` → `v-model`

## 任务流转图

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cron Scheduler                            │
│  每5分钟唤醒 Executor Agent                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Executor Agent                                 │
│  1. GET /api/sub-tasks/available (获取 pending 任务)            │
│  2. FOR EACH task:                                              │
│     a. POST /api/sub-tasks/{id}/claim (认领+自动开始)           │
│     b. 执行任务（创建代码文件）                                    │
│     c. POST /api/sub-tasks/{id}/submit (提交审查)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Reviewer Agent                              │
│  1. GET /api/sub-tasks?status=review                            │
│  2. 审查交付内容                                                 │
│  3. POST /api/review-records (批准/驳回)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Patrol Agent                                │
│  1. 检查超时任务 (in_progress > 30min)                          │
│  2. POST /api/sub-tasks/auto-timeout (自动提交)                │
│  3. 恢复 blocked 任务                                           │
└─────────────────────────────────────────────────────────────────┘
```

## 验证步骤

1. 检查 pending 任务数量应该减少
2. 检查 done 任务数量应该增加
3. 检查 review 任务数量应该增加后减少
4. 验证 GitHub 集成正常工作
