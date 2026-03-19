import logging
from typing import Optional

logger = logging.getLogger(__name__)


PLAN_GENERATION_PROMPT = """## 任务：生成项目执行方案

### 任务信息
- 名称: {task_name}
- 描述: {task_description}
- 类型: {task_type}

### 输出要求

请生成详细的项目执行方案，必须包含以下章节：

1. **项目概述** (必填) - 简述这个任务的目标和背景
2. **技术架构** (必填) - 推荐的技术栈和工具
3. **模块拆分** (必填) - 将任务拆分为哪些子模块/子任务
4. **工作流程** (必填) - 子任务之间的依赖关系和执行顺序
5. 里程碑 - 关键节点和预期完成时间
6. 风险评估 - 可能遇到的问题和应对方案

### 注意事项

- 每个必填章节至少需要 50 字的详细描述
- 不要包含 "TODO"、"待定"、"待补充"、"TBD" 等未完成标记
- 内容总字数不少于 200 字
- 不要使用模糊描述，必须给出具体的方案

请直接输出方案内容，不要包含其他说明。
"""


README_GENERATION_PROMPT = """## 任务：生成 README 文档

### 任务信息
- 名称: {task_name}
- 描述: {task_description}
- 方案: {plan_content}

### 输出要求

请生成标准的 README.md，包含：

1. **项目标题** (# 标题格式)
2. **项目简介** (必填) - 这个任务要做什么
3. **任务状态** (必填) - 使用 - [ ] 待办格式列出所有子任务
4. 进度追踪 - 完成的百分比
5. 团队成员 - 涉及的 Agent 角色

### 注意事项

- 必须包含至少 3 个 - [ ] 待办项（代表子任务）
- 必须有 # 标题
- 内容不少于 100 字
- 不要使用 "TODO"、"待定"、"TBD"

请直接输出 Markdown 内容，不要包含其他说明。
"""


class AIService:
    def __init__(self):
        pass

    def generate_plan_prompt(
        self, task_name: str, task_description: str, task_type: str = "once"
    ) -> str:
        return PLAN_GENERATION_PROMPT.format(
            task_name=task_name, task_description=task_description, task_type=task_type
        )

    def generate_readme_prompt(
        self, task_name: str, task_description: str, plan_content: str
    ) -> str:
        return README_GENERATION_PROMPT.format(
            task_name=task_name,
            task_description=task_description,
            plan_content=plan_content,
        )


def get_ai_service() -> AIService:
    return AIService()
