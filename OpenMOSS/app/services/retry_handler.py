import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class TaskStep(Enum):
    GENERATE_PLAN = "generate_plan"
    GENERATE_README = "generate_readme"
    CREATE_REPO = "create_repo"
    PUSH_README = "push_readme"


@dataclass
class RetryConfig:
    step: TaskStep
    task_id: str
    max_attempts: int
    attempt_count: int


class RetryHandler:
    def __init__(self):
        self.retry_store: Dict[str, RetryConfig] = {}

    def get_key(self, task_id: str, step: TaskStep) -> str:
        return f"{task_id}:{step.value}"

    def should_retry(self, task_id: str, step: TaskStep) -> bool:
        key = self.get_key(task_id, step)
        config = self.retry_store.get(key)

        if not config:
            return True

        return config.attempt_count < config.max_attempts

    def record_attempt(self, task_id: str, step: TaskStep) -> int:
        key = self.get_key(task_id, step)

        if key not in self.retry_store:
            self.retry_store[key] = RetryConfig(
                step=step, task_id=task_id, max_attempts=3, attempt_count=0
            )

        self.retry_store[key].attempt_count += 1
        return self.retry_store[key].attempt_count

    def get_attempt_info(self, task_id: str, step: TaskStep) -> Dict[str, int]:
        key = self.get_key(task_id, step)
        config = self.retry_store.get(key)

        if not config:
            return {"attempt": 0, "max_attempts": 3}

        return {"attempt": config.attempt_count, "max_attempts": config.max_attempts}

    def reset(self, task_id: str, step: TaskStep):
        key = self.get_key(task_id, step)
        if key in self.retry_store:
            del self.retry_store[key]

    def reset_all(self, task_id: str):
        keys_to_delete = [k for k in self.retry_store.keys() if k.startswith(task_id)]
        for key in keys_to_delete:
            del self.retry_store[key]


retry_handler = RetryHandler()
