from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, BigInteger, ForeignKey, Boolean, TIMESTAMP, VARCHAR, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    discord_id = Column(BigInteger, primary_key=True)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires = Column(DateTime, nullable=True)
    github_id = Column(VARCHAR(50), nullable=True, unique=True)
    notion_id = Column(BigInteger, nullable=True, unique=True)
    last_check = Column(TIMESTAMP, nullable=True, default=datetime.now)