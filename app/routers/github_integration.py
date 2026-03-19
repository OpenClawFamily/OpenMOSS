"""
GitHub 集成路由
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_agent, require_role
from app.models.agent import Agent
from app.services import task_service
from app.services.github_service import get_github_service, generate_repo_name
from app.config import AppConfig

router = APIRouter(prefix="/tasks/{task_id}/github", tags=["GitHub Integration"])


class GeneratePlanRequest(BaseModel):
    task_name: str
    task_description: str
    task_type: str = "once"


class GeneratePlanResponse(BaseModel):
    success: bool
    prompt: Optional[str] = None
    content: Optional[str] = None
    validated: bool = False
    error: Optional[str] = None
    attempt: int = 0
    max_attempts: int = 3


class GenerateReadmeRequest(BaseModel):
    task_name: str
    task_description: str
    plan_content: str


class GenerateReadmeResponse(BaseModel):
    success: bool
    prompt: Optional[str] = None
    content: Optional[str] = None
    validated: bool = False
    error: Optional[str] = None
    attempt: int = 0
    max_attempts: int = 3


class CreateRepoResponse(BaseModel):
    success: bool
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    error: Optional[str] = None


class PushReadmeResponse(BaseModel):
    success: bool
    error: Optional[str] = None


class GitHubStatusResponse(BaseModel):
    github_enabled: bool
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    plan_generated: bool = False
    readme_generated: bool = False
    readme_pushed: bool = False
    plan_retry_count: int = 0
    readme_retry_count: int = 0


@router.get(
    "/status", response_model=GitHubStatusResponse, summary="获取 GitHub 集成状态"
)
async def get_github_status(
    task_id: str,
    db: Session = Depends(get_db),
    agent: Agent = Depends(get_current_agent),
):
    config = AppConfig()
    task = task_service.get_task(db, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "github_enabled": config.github_enabled,
        "repo_url": task.github_repo_url,
        "repo_name": task.github_repo_name,
        "plan_generated": task.plan_generated == "true",
        "readme_generated": task.readme_generated == "true",
        "readme_pushed": task.readme_pushed == "true",
        "plan_retry_count": int(task.plan_retry_count or "0"),
        "readme_retry_count": int(task.readme_retry_count or "0"),
    }


@router.post(
    "/create-repo", response_model=CreateRepoResponse, summary="创建 GitHub 仓库"
)
async def create_repo(
    task_id: str,
    db: Session = Depends(get_db),
    agent: Agent = Depends(require_role("planner")),
):
    """为任务创建 GitHub 仓库"""
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用，请在配置中开启")

    github_service = get_github_service(config.github_config)
    if not github_service:
        raise HTTPException(status_code=500, detail="GitHub 服务初始化失败")

    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果仓库已存在，直接返回
    if task.github_repo_url:
        return {
            "success": True,
            "repo_url": task.github_repo_url,
            "repo_name": task.github_repo_name,
        }

    # 生成仓库名称
    repo_name = generate_repo_name(task.name, task.id)

    try:
        result = github_service.create_repo(
            name=repo_name, description=f"OpenMOSS 任务: {task.name}", private=True
        )
        repo_url = result.get("html_url", "")

        # 更新任务信息
        task_service.update_task_github_info(
            db, task_id, repo_url=repo_url, repo_name=repo_name
        )

        return {
            "success": True,
            "repo_url": repo_url,
            "repo_name": repo_name,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建仓库失败: {str(e)}")


@router.post(
    "/push-readme", response_model=PushReadmeResponse, summary="推送 README 到 GitHub"
)
async def push_readme(
    task_id: str,
    db: Session = Depends(get_db),
    agent: Agent = Depends(require_role("planner")),
):
    """推送 README 到 GitHub 仓库"""
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用，请在配置中开启")

    github_service = get_github_service(config.github_config)
    if not github_service:
        raise HTTPException(status_code=500, detail="GitHub 服务初始化失败")

    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if not task.github_repo_name:
        raise HTTPException(status_code=400, detail="请先创建 GitHub 仓库")

    if not task.readme_content:
        raise HTTPException(status_code=400, detail="请先生成 README 内容")

    try:
        github_service.create_file(
            repo=task.github_repo_name,
            path="README.md",
            content=task.readme_content,
            message="Add README via OpenMOSS",
        )

        # 标记 README 已推送
        task_service.mark_readme_pushed(db, task_id)

        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推送 README 失败: {str(e)}")


@router.post(
    "/generate-readme", response_model=GenerateReadmeResponse, summary="AI 生成 README"
)
async def generate_readme(
    task_id: str,
    req: GenerateReadmeRequest,
    db: Session = Depends(get_db),
    agent: Agent = Depends(require_role("planner")),
):
    """AI 生成 README 内容"""
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用，请在配置中开启")

    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 简单的 README 生成（基于任务信息）
    readme_content = f"""# {req.task_name}

{req.task_description}

## 项目方案

{req.plan_content}

## 任务信息

- 任务类型: {req.task_type}
- 任务 ID: {task_id}

---
*Generated by OpenMOSS*
"""

    # 保存 README 内容
    task_service.update_task_readme(db, task_id, readme_content, True)

    return {
        "success": True,
        "content": readme_content,
        "validated": True,
        "attempt": 0,
        "max_attempts": 3,
    }


@router.post(
    "/generate-plan", response_model=GeneratePlanResponse, summary="AI 生成项目方案"
)
async def generate_plan(
    task_id: str,
    req: GeneratePlanRequest,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    """AI 生成项目方案"""
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用，请在配置中开启")

    # 简单的方案生成（基于任务信息）
    plan_content = f"""## 项目概述

本项目旨在完成任务：{req.task_name}

{req.task_description}

## 任务类型

{req.task_type}

## 目标

1. 完成核心功能开发
2. 确保代码质量
3. 编写相关文档
"""

    # 保存方案内容
    task_service.update_task_plan(db, task_id, plan_content, True)

    return {
        "success": True,
        "content": plan_content,
        "validated": True,
        "attempt": 0,
        "max_attempts": 3,
    }
