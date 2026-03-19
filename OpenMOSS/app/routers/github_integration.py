from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.auth.dependencies import get_current_agent, require_role
from app.models.agent import Agent
from app.services import task_service
from app.services.validator import PlanValidator, ReadmeValidator, RepoInfoValidator
from app.services.github_service import get_github_service, generate_repo_name
from app.services.ai_service import get_ai_service
from app.services.retry_handler import retry_handler, TaskStep
from app.services.notification_service import get_notification_service
from app.config import AppConfig

logger = logging.getLogger(__name__)
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
        "plan_generated": task.plan_generated,
        "readme_generated": task.readme_generated,
        "readme_pushed": task.readme_pushed,
        "plan_retry_count": int(task.plan_retry_count or "0"),
        "readme_retry_count": int(task.readme_retry_count or "0"),
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
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用，请在配置中开启")

    ai_service = get_ai_service()
    prompt = ai_service.generate_plan_prompt(
        req.task_name, req.task_description, req.task_type
    )

    return {
        "success": True,
        "prompt": prompt,
        "content": None,
        "validated": False,
    }


class SubmitPlanRequest(BaseModel):
    content: str = Field(..., description="AI 生成的方案内容")


class SubmitReadmeRequest(BaseModel):
    content: str = Field(..., description="AI 生成的 README 内容")


@router.post(
    "/submit-plan",
    response_model=GeneratePlanResponse,
    summary="提交方案内容（AI 生成后调用）",
)
async def submit_plan(
    task_id: str,
    req: SubmitPlanRequest,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    content = req.content
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    validator = PlanValidator()
    valid, error = validator.validate(content)

    if valid:
        task_service.update_task_plan(db, task_id, content, True)
        retry_handler.reset(task_id, TaskStep.GENERATE_PLAN)

        return {
            "success": True,
            "content": content,
            "validated": True,
            "attempt": 0,
            "max_attempts": 3,
        }

    attempt = retry_handler.record_attempt(task_id, TaskStep.GENERATE_PLAN)
    task_service.increment_retry_count(db, task_id, "plan")

    attempt_info = retry_handler.get_attempt_info(task_id, TaskStep.GENERATE_PLAN)

    if not retry_handler.should_retry(task_id, TaskStep.GENERATE_PLAN):
        notification_service = get_notification_service()
        import asyncio

        asyncio.create_task(
            notification_service.send_task_failure_notification(
                task_id=task_id,
                task_name=task.name,
                step="generate_plan",
                error=error,
                attempts=attempt,
            )
        )

        task_service.update_task_status(db, task_id, "failed")

        raise HTTPException(
            status_code=400,
            detail={
                "error": f"方案验证连续失败，已通知管理员",
                "final_error": error,
                "attempts": attempt,
            },
        )

    return {
        "success": False,
        "error": error,
        "validated": False,
        "attempt": attempt_info["attempt"],
        "max_attempts": attempt_info["max_attempts"],
        "message": f"方案验证失败，请重新生成 (第 {attempt}/{attempt_info['max_attempts']} 次)",
    }


@router.post(
    "/create-repo", response_model=CreateRepoResponse, summary="创建 GitHub 仓库"
)
async def create_github_repo(
    task_id: str,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用")

    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if not task.plan_content:
        raise HTTPException(status_code=400, detail="请先生成方案")

    if task.github_repo_url:
        return {
            "success": True,
            "repo_url": task.github_repo_url,
            "repo_name": task.github_repo_name,
            "message": "仓库已存在",
        }

    github_service = get_github_service(config.github_config)
    if not github_service:
        raise HTTPException(status_code=500, detail="GitHub 服务初始化失败")

    try:
        repo_name = generate_repo_name(task.name, task.id)

        validator = RepoInfoValidator()
        valid, error = validator.validate_repo_name(repo_name)
        if not valid:
            raise HTTPException(status_code=400, detail=f"仓库名称无效: {error}")

        result = github_service.create_repo(
            name=repo_name, description=f"OpenMOSS 任务: {task.name}", private=True
        )

        repo_url = result.get("html_url")
        task_service.update_task_github_info(
            db, task_id, repo_url=repo_url, repo_name=repo_name, status="preparing"
        )

        retry_handler.reset(task_id, TaskStep.CREATE_REPO)

        return {
            "success": True,
            "repo_url": repo_url,
            "repo_name": repo_name,
        }

    except ValueError as e:
        logger.error(f"GitHub 仓库创建失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"GitHub 仓库创建异常: {e}")
        raise HTTPException(status_code=500, detail=f"仓库创建失败: {str(e)}")


@router.post(
    "/generate-readme", response_model=GenerateReadmeResponse, summary="AI 生成 README"
)
async def generate_readme(
    task_id: str,
    req: GenerateReadmeRequest,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用")

    ai_service = get_ai_service()
    prompt = ai_service.generate_readme_prompt(
        req.task_name, req.task_description, req.plan_content
    )

    return {
        "success": True,
        "prompt": prompt,
        "content": None,
        "validated": False,
    }


@router.post(
    "/submit-readme",
    response_model=GenerateReadmeResponse,
    summary="提交 README 内容（AI 生成后调用）",
)
async def submit_readme(
    task_id: str,
    req: SubmitReadmeRequest,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    content = req.content
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    validator = ReadmeValidator()
    valid, error = validator.validate(content)

    if valid:
        task_service.update_task_readme(db, task_id, content, True)
        retry_handler.reset(task_id, TaskStep.GENERATE_README)

        return {
            "success": True,
            "content": content,
            "validated": True,
            "attempt": 0,
            "max_attempts": 3,
        }

    attempt = retry_handler.record_attempt(task_id, TaskStep.GENERATE_README)
    task_service.increment_retry_count(db, task_id, "readme")

    attempt_info = retry_handler.get_attempt_info(task_id, TaskStep.GENERATE_README)

    if not retry_handler.should_retry(task_id, TaskStep.GENERATE_README):
        notification_service = get_notification_service()
        import asyncio

        asyncio.create_task(
            notification_service.send_task_failure_notification(
                task_id=task_id,
                task_name=task.name,
                step="generate_readme",
                error=error,
                attempts=attempt,
            )
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": f"README 验证连续失败，已通知管理员",
                "final_error": error,
                "attempts": attempt,
            },
        )

    return {
        "success": False,
        "error": error,
        "validated": False,
        "attempt": attempt_info["attempt"],
        "max_attempts": attempt_info["max_attempts"],
        "message": f"README 验证失败，请重新生成 (第 {attempt}/{attempt_info['max_attempts']} 次)",
    }


@router.post(
    "/push-readme", response_model=PushReadmeResponse, summary="推送 README 到 GitHub"
)
async def push_readme(
    task_id: str,
    agent: Agent = Depends(require_role("planner")),
    db: Session = Depends(get_db),
):
    config = AppConfig()

    if not config.github_enabled:
        raise HTTPException(status_code=400, detail="GitHub 集成未启用")

    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if not task.readme_content:
        raise HTTPException(status_code=400, detail="请先生成 README")

    if not task.github_repo_url:
        raise HTTPException(status_code=400, detail="请先创建 GitHub 仓库")

    if task.readme_pushed:
        return {
            "success": True,
            "message": "README 已推送",
        }

    github_service = get_github_service(config.github_config)
    if not github_service:
        raise HTTPException(status_code=500, detail="GitHub 服务初始化失败")

    try:
        github_service.create_file(
            repo=task.github_repo_name,
            path="README.md",
            content=task.readme_content,
            message="chore: 初始化 README (OpenMOSS)",
        )

        task_service.mark_readme_pushed(db, task_id)
        task_service.update_task_status(db, task_id, "active")

        retry_handler.reset_all(task_id)

        return {"success": True}

    except Exception as e:
        logger.error(f"README 推送失败: {e}")
        raise HTTPException(status_code=500, detail=f"推送失败: {str(e)}")
