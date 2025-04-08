import json
from datetime import date, datetime, time

from sqlalchemy import (TIMESTAMP, VARCHAR, BigInteger, Boolean, Column,
                        DateTime, ForeignKey, Integer, String, Text, inspect)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def todict(self, exclude=None, datetime_format="%Y-%m-%d %H:%M:%S"):
        exclude = exclude or []
        result = {}
        for c in inspect(self).mapper.column_attrs:
            if c.key in exclude:
                continue
            value = getattr(self, c.key)
            if isinstance(value, (datetime, date, time)):
                value = value.strftime(datetime_format)
            result[c.key] = value
        return result


class User(Base):
    __tablename__ = "user"
    discord_id = Column(BigInteger, primary_key=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires = Column(DateTime, nullable=True)
    last_check = Column(TIMESTAMP, nullable=True, default=datetime.now)


class Github(Base):
    __tablename__ = "github"
    github_id = Column(BigInteger, primary_key=True)  # github id
    discord_id = Column(
        BigInteger, ForeignKey("user.discord_id", ondelete="CASCADE")
    )  # discord id
    github_login = Column(Text, nullable=False)


class Notion(Base):
    __tablename__ = "notion"
    notion_id = Column(BigInteger, primary_key=True)  # notion id
    discord_id = Column(
        BigInteger, ForeignKey("user.discord_id", ondelete="CASCADE")
    )  # discord id
    notion_login = Column(Text, nullable=False)
