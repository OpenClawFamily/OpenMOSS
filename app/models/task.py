"""
任务表模型
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime

from app.database import Base


class Task(Base):
    __tablename__ = "task"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, comment="任务名称")
    description = Column(Text, default="", comment="任务描述")
    type = Column(String(20), default="once", comment="任务类型: once/recurring")
    status = Column(String(20), default="planning", index=True, comment="状态: planning/active/in_progress/completed/archived")
    # GitHub 集成字段
    github_repo_url = Column(String(500), nullable=True, comment="GitHub 仓库地址")
    github_repo_name = Column(String(200), nullable=True, comment="GitHub 仓库名称")
    plan_content = Column(Text, nullable=True, comment="项目方案内容")
    plan_generated = Column(String(10), default="false", comment="方案是否已生成")
    readme_content = Column(Text, nullable=True, comment="README 内容")
    readme_generated = Column(String(10), default="false", comment="README 是否已生成")
    readme_pushed = Column(String(10), default="false", comment="README 是否已推送")
    plan_retry_count = Column(String(10), default="0", comment="方案生成重试次数")
    readme_retry_count = Column(String(10), default="0", comment="README 生成重试次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
