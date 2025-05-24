import json
from datetime import date, datetime, time

from sqlalchemy import (TIMESTAMP, VARCHAR, BigInteger, Boolean, Column,
                        DateTime, ForeignKey, Integer, Text, UniqueConstraint,
                        inspect, JSON, Float, String, Table, func)
from sqlalchemy.orm import relationship

try:
    from .basemodel import Base
except ImportError:
    from basemodel import Base

role_assignments = Table(
    "role_assignments",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.role_id"),
        primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("github.github_id"),
        primary_key=True),
)

class User(Base):
    __tablename__ = "user"
    discord_id = Column(BigInteger, primary_key=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires = Column(DateTime, nullable=True)
    last_check = Column(TIMESTAMP, nullable=True, default=datetime.now)

    github_accounts = relationship(
        "Github", back_populates="user", cascade="all, delete-orphan"
    )
    notion_accounts = relationship(
        "Notion", back_populates="user", cascade="all, delete-orphan"
    )


class Github(Base):
    __tablename__ = "github"
    github_id = Column(BigInteger, primary_key=True)  # GitHub user ID (or developer ID)
    discord_id = Column(BigInteger, ForeignKey("user.discord_id"), nullable=False)

    github_login = Column(Text, nullable=False)       # 깃허브 로그인명 (기존 Github 모델)
    github_url = Column(String, unique=True, nullable=False)
    primary_languages = Column(JSON, nullable=False)
    experience_years = Column(Float, nullable=False)
    public_repos = Column(Integer, nullable=False)
    total_stars = Column(Integer, nullable=False)
    total_forks = Column(Integer, nullable=False)
    profile_created_at = Column(DateTime, nullable=False)
    last_active_date = Column(DateTime, nullable=True)

    repositories = relationship("Repository", back_populates="owner")
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=True)
    projects = relationship("Project", back_populates="owner")
    roles_assigned = relationship(
        "Role", secondary=role_assignments, back_populates="assigned_users"
    )


class Notion(Base):
    __tablename__ = "notion"
    notion_id = Column(BigInteger, primary_key=True)
    discord_id = Column(
        BigInteger,
        ForeignKey(
            "user.discord_id",
            ondelete="CASCADE"))
    notion_login = Column(Text, nullable=False)

    user = relationship("User", back_populates="notion_accounts")


class ServerInfo(Base):
    __tablename__ = "server_info"
    server_id = Column(BigInteger, primary_key=True)
    mod_id = Column(BigInteger, nullable=True)
    notion_token = Column(Text, nullable=True)
    webhook_channel_id = Column(BigInteger, nullable=True)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    notion_databases = relationship(
        "NotionDatabase", back_populates="server", cascade="all, delete-orphan"
    )
    notion_tags = relationship(
        "NotionTags", back_populates="server", cascade="all, delete-orphan"
    )

    def todict(self, exclude=None, datetime_format="%Y-%m-%d %H:%M:%S"):
        result = super().todict(exclude, datetime_format)
        result["notion_databases"] = [
            {
                "database_id": db.database_id,
                "database_name": db.database_name,
                "channel_id": db.channel_id,
            }
            for db in self.notion_databases
        ]
        result["notion_tags"] = [
            {"idx": tag.idx, "tag": tag.tag} for tag in self.notion_tags
        ]
        return result


class NotionDatabase(Base):
    __tablename__ = "notion_database"
    server_id = Column(
        BigInteger, ForeignKey("server_info.server_id", ondelete="CASCADE")
    )
    channel_id = Column(BigInteger, nullable=False)
    database_id = Column(VARCHAR(40), primary_key=True)
    database_name = Column(Text, nullable=True)

    server = relationship("ServerInfo", back_populates="notion_databases")
    pages = relationship(
        "NotionPages", back_populates="database", cascade="all, delete-orphan"
    )


class NotionPages(Base):
    __tablename__ = "notion_pages"
    page_id = Column(VARCHAR(40), primary_key=True)
    database_id = Column(
        VARCHAR(40),
        ForeignKey(
            "notion_database.database_id",
            ondelete="CASCADE"))
    thread_id = Column(BigInteger, nullable=True)
    updated = Column(Boolean, nullable=False, default=False)
    blocked = Column(Boolean, nullable=False, default=False)

    database = relationship("NotionDatabase", back_populates="pages")


class NotionTags(Base):
    __tablename__ = "notion_tags"
    idx = Column(Integer, primary_key=True, autoincrement=True)
    server_id = Column(
        BigInteger, ForeignKey("server_info.server_id", ondelete="CASCADE")
    )
    tag = Column(VARCHAR(100), nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "server_id",
            "tag",
            name="uq_server_tag"),
    )
    server = relationship("ServerInfo", back_populates="notion_tags")


class Repository(Base):
    __tablename__ = "repositories"

    repo_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("github.github_id"), nullable=False)

    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    primary_language = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    forks = Column(Integer, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=True)  # 프로젝트 분야 태그
    core_features = Column(JSON, nullable=True)  # 레포지토리 주요 기능들

    owner = relationship("Github", back_populates="repositories")

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("github.github_id"), nullable=True)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    team_size = Column(Integer, nullable=True)
    core_features = Column(JSON, nullable=False)
    tech_stack = Column(JSON, nullable=False)
    complexity = Column(String, nullable=False)
    database = Column(String, nullable=True)
    platform = Column(String, nullable=False)
    notifications = Column(Boolean, default=False)
    map_integration = Column(Boolean, default=False)
    auth_required = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("Github", back_populates="projects")
    roles = relationship(
        "Role",
        back_populates="project",
        cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.project_id"),
        nullable=False)

    name = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    languages_tools = Column(
        JSON, nullable=True
    )  # Required programming languages for the role

    # project = relationship("Project", back_populates="roles") 우선 role->proj 단방향으로 설
    # 연결 테이블을 통해 할당된 사용자 목록을 관리합니다.
    assigned_users = relationship(
        "Github", secondary=role_assignments, back_populates="roles_assigned"
    )