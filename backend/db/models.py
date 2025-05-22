import json
from datetime import date, datetime, time

from sqlalchemy import (TIMESTAMP, VARCHAR, BigInteger, Boolean, Column,
                        DateTime, ForeignKey, Integer, String, Text, inspect)
from sqlalchemy.orm import relationship

from .basemodel import Base

class User(Base):
    __tablename__ = "user"
    discord_id = Column(BigInteger, primary_key=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires = Column(DateTime, nullable=True)
    last_check = Column(TIMESTAMP, nullable=True, default=datetime.now)

    github_accounts = relationship("Github", back_populates="user", cascade="all, delete-orphan")
    notion_accounts = relationship("Notion", back_populates="user", cascade="all, delete-orphan")


class Github(Base):
    __tablename__ = "github"
    github_id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, ForeignKey("user.discord_id", ondelete="CASCADE"))
    github_login = Column(Text, nullable=False)

    user = relationship("User", back_populates="github_accounts")


class Notion(Base):
    __tablename__ = "notion"
    notion_id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, ForeignKey("user.discord_id", ondelete="CASCADE"))
    notion_login = Column(Text, nullable=False)

    user = relationship("User", back_populates="notion_accounts")


class ServerInfo(Base):
    __tablename__ = "server_info"
    server_id = Column(BigInteger, primary_key=True)
    mod_id = Column(BigInteger, nullable=True)
    notion_token = Column(Text, nullable=True)
    webhook_channel_id = Column(BigInteger, nullable=True)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    notion_databases = relationship("NotionDatabase", back_populates="server", cascade="all, delete-orphan")


class NotionDatabase(Base):
    __tablename__ = "notion_database"
    server_id = Column(BigInteger, ForeignKey("server_info.server_id", ondelete="CASCADE"))
    channel_id = Column(BigInteger, nullable=False)
    database_id = Column(VARCHAR(40), primary_key=True)

    server = relationship("ServerInfo", back_populates="notion_databases")
    pages = relationship("NotionPages", back_populates="database", cascade="all, delete-orphan")


class NotionPages(Base):
    __tablename__ = "notion_pages"
    page_id = Column(VARCHAR(40), primary_key=True)
    database_id = Column(VARCHAR(40), ForeignKey("notion_database.database_id", ondelete="CASCADE"))
    thread_id = Column(BigInteger, nullable=True)
    updated = Column(Boolean, nullable=False, default=False)

    database = relationship("NotionDatabase", back_populates="pages")