import logging
from typing import Optional, Dict, Any, List
import httpx

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            from app.config import AppConfig

            config = AppConfig().raw.get("notification", {})

        self.enabled = config.get("enabled", False)
        self.channels: List[str] = config.get("channels", [])
        self.events: List[str] = config.get("events", [])

    def is_enabled(self) -> bool:
        return self.enabled and len(self.channels) > 0

    async def send_task_failure_notification(
        self, task_id: str, task_name: str, step: str, error: str, attempts: int
    ):
        if not self.is_enabled():
            logger.warning("通知未启用，跳过发送失败通知")
            return

        message = self._format_failure_message(
            task_id=task_id,
            task_name=task_name,
            step=step,
            error=error,
            attempts=attempts,
        )

        for channel in self.channels:
            try:
                await self._send_to_channel(channel, message)
            except Exception as e:
                logger.error(f"发送通知到 {channel} 失败: {e}")

    def _format_failure_message(
        self, task_id: str, task_name: str, step: str, error: str, attempts: int
    ) -> str:
        step_names = {
            "generate_plan": "生成项目方案",
            "generate_readme": "生成 README",
            "create_repo": "创建 GitHub 仓库",
            "push_readme": "推送 README",
        }

        step_display = step_names.get(step, step)

        return f"""
🚨 **任务执行失败**

**任务**: {task_name}
**ID**: {task_id}
**失败步骤**: {step_display}
**重试次数**: {attempts}/3
**失败原因**: {error}

请检查任务配置后重新尝试。
"""

    async def _send_to_channel(self, channel: str, message: str):
        if channel.startswith("chat:"):
            await self._send_to_feishu(channel[5:], message)
        elif channel.startswith("telegram:"):
            await self._send_to_telegram(channel[9:], message)
        elif "@" in channel:
            await self._send_to_email(channel, message)

    async def _send_to_feishu(self, chat_id: str, message: str):
        logger.info(f"发送飞书通知到 {chat_id}: {message[:100]}...")

    async def _send_to_telegram(self, chat_id: str, message: str):
        logger.info(f"发送 Telegram 通知到 {chat_id}: {message[:100]}...")

    async def _send_to_email(self, email: str, message: str):
        logger.info(f"发送邮件通知到 {email}: {message[:100]}...")


def get_notification_service() -> NotificationService:
    return NotificationService()
