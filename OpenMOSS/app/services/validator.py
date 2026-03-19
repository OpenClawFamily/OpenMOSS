import re
from typing import Tuple


class PlanValidator:
    REQUIRED_SECTIONS = [
        "项目概述",
        "技术架构",
        "模块拆分",
        "工作流程",
    ]

    MIN_LENGTH = 200
    MAX_LENGTH = 10000

    def validate(self, content: str) -> Tuple[bool, str]:
        if not content or not content.strip():
            return False, "方案内容不能为空"

        content = content.strip()

        if len(content) < self.MIN_LENGTH:
            return False, f"方案内容过短 (至少 {self.MIN_LENGTH} 字)"

        if len(content) > self.MAX_LENGTH:
            return False, f"方案内容过长 (最多 {self.MAX_LENGTH} 字)"

        missing = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                missing.append(section)

        if missing:
            return False, f"缺少必需章节: {', '.join(missing)}"

        if content.count("\n") < 5:
            return False, "方案内容过于简单，需要更详细的描述"

        forbidden = ["TODO", "待定", "待补充", "TBD"]
        found = [f for f in forbidden if f in content]
        if found:
            return False, f"方案包含未完成标记: {', '.join(found)}"

        return True, ""


class ReadmeValidator:
    REQUIRED_SECTIONS = [
        "项目简介",
        "任务状态",
    ]

    MIN_LENGTH = 100
    MAX_LENGTH = 5000

    def validate(self, content: str) -> Tuple[bool, str]:
        if not content or not content.strip():
            return False, "README 内容不能为空"

        content = content.strip()

        if len(content) < self.MIN_LENGTH:
            return False, f"README 内容过短 (至少 {self.MIN_LENGTH} 字)"

        if len(content) > self.MAX_LENGTH:
            return False, f"README 内容过长 (最多 {self.MAX_LENGTH} 字)"

        missing = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                missing.append(section)

        if missing:
            return False, f"缺少必需章节: {', '.join(missing)}"

        if "# " not in content:
            return False, "README 必须包含标题 (# 格式)"

        if "- [" not in content:
            return False, "README 必须包含待办列表 (- [ ] 格式)"

        return True, ""


class RepoInfoValidator:
    REPO_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
    MIN_NAME_LENGTH = 3
    MAX_NAME_LENGTH = 100

    def validate_repo_name(self, name: str) -> Tuple[bool, str]:
        if not name:
            return False, "仓库名称不能为空"

        name = name.strip()

        if len(name) < self.MIN_NAME_LENGTH:
            return False, f"仓库名称过短 (至少 {self.MIN_NAME_LENGTH} 字符)"

        if len(name) > self.MAX_NAME_LENGTH:
            return False, f"仓库名称过长 (最多 {self.MAX_NAME_LENGTH} 字符)"

        if not self.REPO_NAME_PATTERN.match(name):
            return False, "仓库名称只能包含小写字母、数字和连字符，且以字母或数字开头"

        return True, ""

    def validate_repo_url(self, url: str) -> Tuple[bool, str]:
        if not url:
            return False, "仓库 URL 不能为空"

        url = url.strip()

        if not url.startswith("https://github.com/"):
            return False, "必须是 GitHub 仓库地址"

        return True, ""
