"""Pydantic 请求/响应模型。"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MemoryCategory(str, Enum):
    MEDITATION_EXPERIENCE = "meditation_experience"
    EMOTION_PATTERN = "emotion_pattern"
    PERSONAL_PREFERENCE = "personal_preference"
    GOAL_PROGRESS = "goal_progress"
    IMPORTANT_EVENT = "important_event"
    HEALTH_NOTE = "health_note"
    LIFE_CONTEXT = "life_context"


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str
    memory_updated: bool = False


class WxLoginRequest(BaseModel):
    code: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nickname: Optional[str] = None


class MemoryItem(BaseModel):
    id: str
    category: MemoryCategory
    content: str
    summary: str
    importance: float = 0.0
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    memories: list[MemoryItem]
    total: int


class KnowledgeImportRequest(BaseModel):
    content: str = Field(..., min_length=1)
    title: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    parent_id: Optional[str] = None


class KnowledgeImportFileRequest(BaseModel):
    filename: str
    tags: list[str] = Field(default_factory=list)
    parent_id: Optional[str] = None


class KnowledgeItem(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    tags: list[str]
    parent_id: Optional[str] = None
    created_at: datetime


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5


class KnowledgeSearchResult(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    score: float
    tags: list[str]


class KnowledgeSearchResponse(BaseModel):
    results: list[KnowledgeSearchResult]


class UserProfile(BaseModel):
    user_id: str
    nickname: Optional[str] = None
    created_at: datetime
    total_conversations: int = 0
    total_messages: int = 0
    memory_summary: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class StreamChunk(BaseModel):
    delta: str
    done: bool = False
    conversation_id: Optional[str] = None
