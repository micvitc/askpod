from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)


class PodcastSession(Base):
    __tablename__ = "podcast_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    pdf_path = Column(String)
    audio_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
