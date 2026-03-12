import base64
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self, token: str, org: Optional[str] = None):
        self.token = token
        self.org = org
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def create_repo(
        self, name: str, description: str, private: bool = True
    ) -> Dict[str, Any]:
        url = (
            f"{self.base_url}/repos/{self.org}/{name}"
            if self.org
            else f"{self.base_url}/user/repos"
        )

        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True,
            "default_branch": "main",
        }

        with httpx.Client() as client:
            response = client.post(url, json=data, headers=self._get_headers())

            if response.status_code == 201:
                return response.json()
            elif response.status_code == 422:
                error_data = response.json()
                if "name" in error_data.get("errors", [{}])[0]:
                    raise ValueError(f"仓库名称 '{name}' 已存在")
                raise ValueError(
                    f"仓库创建失败: {error_data.get('message', '未知错误')}"
                )
            else:
                raise ValueError(
                    f"GitHub API 错误: {response.status_code} - {response.text}"
                )

    def get_repo(self, name: str) -> Dict[str, Any]:
        url = (
            f"{self.base_url}/repos/{self.org}/{name}"
            if self.org
            else f"{self.base_url}/repos/{name}"
        )

        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers())

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise ValueError(f"仓库 '{name}' 不存在")
            else:
                raise ValueError(f"GitHub API 错误: {response.status_code}")

    def create_file(
        self, repo: str, path: str, content: str, message: str, branch: str = "main"
    ) -> Dict[str, Any]:
        url = (
            f"{self.base_url}/repos/{self.org}/{repo}/contents/{path}"
            if self.org
            else f"{self.base_url}/repos/{repo}/contents/{path}"
        )

        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        data = {"message": message, "content": encoded_content, "branch": branch}

        with httpx.Client() as client:
            response = client.put(url, json=data, headers=self._get_headers())

            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise ValueError(
                    f"文件推送失败: {response.status_code} - {response.text}"
                )

    def update_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        sha: str,
        branch: str = "main",
    ) -> Dict[str, Any]:
        url = (
            f"{self.base_url}/repos/{self.org}/{repo}/contents/{path}"
            if self.org
            else f"{self.base_url}/repos/{repo}/contents/{path}"
        )

        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch,
        }

        with httpx.Client() as client:
            response = client.put(url, json=data, headers=self._get_headers())

            if response.status_code in [200, 201]:
                return response.json()
            else:
                raise ValueError(
                    f"文件更新失败: {response.status_code} - {response.text}"
                )

    def get_file_content(
        self, repo: str, path: str, branch: str = "main"
    ) -> Optional[str]:
        url = (
            f"{self.base_url}/repos/{self.org}/{repo}/contents/{path}"
            if self.org
            else f"{self.base_url}/repos/{repo}/contents/{path}"
        )

        params = {"ref": branch}

        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers(), params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("encoding") == "base64":
                    return base64.b64decode(data["content"]).decode("utf-8")
            return None

    def list_repos(self, per_page: int = 30) -> list:
        if self.org:
            url = f"{self.base_url}/orgs/{self.org}/repos"
        else:
            url = f"{self.base_url}/user/repos"

        params = {"per_page": per_page, "sort": "updated"}

        with httpx.Client() as client:
            response = client.get(url, headers=self._get_headers(), params=params)

            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError(f"获取仓库列表失败: {response.status_code}")


def get_github_service(config: Optional[dict] = None) -> Optional[GitHubService]:
    if not config:
        from app.config import AppConfig

        config = AppConfig().raw.get("github", {})

    if not config or not config.get("enabled"):
        return None

    token = config.get("token")
    if not token:
        return None

    org = config.get("org")

    return GitHubService(token=token, org=org)


def generate_repo_name(task_name: str, task_id: str) -> str:
    import re

    clean_name = re.sub(r"[^\w\s-]", "", task_name)
    clean_name = re.sub(r"[-\s]+", "-", clean_name)
    clean_name = clean_name.strip("-").lower()

    short_id = task_id[:8]

    return f"openmoss-{clean_name}-{short_id}"
