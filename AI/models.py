from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    developer_id       = Column(Integer, primary_key=True, autoincrement=True)
    name               = Column(String, nullable=False)
    github_url         = Column(String, unique=True, nullable=False)
    primary_languages  = Column(JSON, nullable=False)
    experience_years   = Column(Float, nullable=False)
    public_repos       = Column(Integer, nullable=False)
    total_stars        = Column(Integer, nullable=False)
    total_forks        = Column(Integer, nullable=False)
    profile_created_at = Column(DateTime, nullable=False)
    last_active_date   = Column(DateTime, nullable=True)

    repositories = relationship("Repository", back_populates="owner")
    projects     = relationship("Project", back_populates="owner")

class Repository(Base):
    __tablename__ = "repositories"
    repo_id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.developer_id"), nullable=False)
    name             = Column(String, nullable=False)
    url              = Column(String, unique=True, nullable=False)
    primary_language = Column(String, nullable=True)
    stars            = Column(Integer, nullable=False)
    forks            = Column(Integer, nullable=False)
    description      = Column(Text)
    category           = Column(String, nullable=True)     # 프로젝트 분야 태그
    core_features      = Column(JSON, nullable=True)       # 레포지토리 주요 기능들

    owner = relationship("User", back_populates="repositories")

class Project(Base):
    __tablename__ = "projects"

    project_id      = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(String, nullable=False)
    description     = Column(Text, nullable=False)
    category        = Column(String, nullable=True)      
    team_size       = Column(Integer, nullable=True)     
    core_features   = Column(JSON, nullable=False)
    tech_stack      = Column(JSON, nullable=False)
    complexity      = Column(String, nullable=False)
    database        = Column(String, nullable=True)
    platform        = Column(String, nullable=False)
    notifications   = Column(Boolean, default=False)
    map_integration = Column(Boolean, default=False)
    auth_required   = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.developer_id"), nullable=True)
    owner    = relationship("User", back_populates="projects")



class Role(Base):
    __tablename__ = "roles"

    role_id     = Column(Integer, primary_key=True, autoincrement=True)
    project_id  = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    name        = Column(String, nullable=False)
    count       = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    languages_tools  = Column(JSON, nullable=True)   # Required programming languages for the role

    project = relationship("Project", back_populates="roles")

# Establish 1:N relationship between Project and Role
Project.roles = relationship(
    "Role",
    back_populates="project",
    cascade="all, delete-orphan"
)

