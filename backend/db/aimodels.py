from datetime import datetime

from basemodel import Base
from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Table, Text)
from sqlalchemy.orm import declarative_base, relationship

# Association table: 역할과 사용자 간의 다대다 관계를 표현
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
        ForeignKey("users.developer_id"),
        primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    project_id = Column(
        Integer,
        ForeignKey("projects.project_id"),
        nullable=True)
    developer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    github_url = Column(String, unique=True, nullable=False)
    primary_languages = Column(JSON, nullable=False)
    experience_years = Column(Float, nullable=False)
    public_repos = Column(Integer, nullable=False)
    total_stars = Column(Integer, nullable=False)
    total_forks = Column(Integer, nullable=False)
    profile_created_at = Column(DateTime, nullable=False)
    last_active_date = Column(DateTime, nullable=True)

    repositories = relationship("Repository", back_populates="owner")
    # 단순히 project_id로 연결된 프로젝트를 참조할 수도 있도록 추가
    project = relationship("Project", foreign_keys=[project_id])
    # 사용자별로 어떤 역할을 맡고 있는지 연결 테이블을 통해 참조
    roles_assigned = relationship(
        "Role", secondary=role_assignments, back_populates="assigned_users"
    )


class Repository(Base):
    __tablename__ = "repositories"

    repo_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.developer_id"), nullable=False)

    name = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    primary_language = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    forks = Column(Integer, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=True)  # 프로젝트 분야 태그
    core_features = Column(JSON, nullable=True)  # 레포지토리 주요 기능들

    owner = relationship("User", back_populates="repositories")


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.developer_id"), nullable=True)

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

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
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
        "User", secondary=role_assignments, back_populates="roles_assigned"
    )
