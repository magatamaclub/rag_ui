from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Enum as SQLEnum,
    Text,
)
from sqlalchemy.sql import func
from enum import Enum
from .database import Base


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class DifyAppType(str, Enum):
    WORKFLOW = "workflow"
    CHATFLOW = "chatflow"
    CHATBOT = "chatbot"
    AGENT = "agent"
    TEXT_GENERATOR = "text_generator"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DifyConfig(Base):
    __tablename__ = "dify_configs"

    id = Column(Integer, primary_key=True, index=True)
    api_url = Column(String, unique=True, index=True)
    api_key = Column(String)


class DifyApp(Base):
    __tablename__ = "dify_apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    app_type = Column(SQLEnum(DifyAppType), nullable=False)
    api_key = Column(String, nullable=False)
    api_url = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
