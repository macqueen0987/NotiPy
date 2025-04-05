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
    last_check = Column(TIMESTAMP, nullable=True, default=datetime.now)

class Github(Base):
    __tablename__ = 'github'
    id = Column(BigInteger, primary_key=True)  # github id
    discord_id = Column(BigInteger, ForeignKey('user.discord_id', ondelete='CASCADE'))  # discord id
    login = Column(Text, nullable=False)

class Notion(Base):
    __tablename__ = 'notion'
    id = Column(BigInteger, primary_key=True)  # notion id
    discord_id = Column(BigInteger, ForeignKey('user.discord_id', ondelete='CASCADE'))  # discord id
    login = Column(Text, nullable=False)
