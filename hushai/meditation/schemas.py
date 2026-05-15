"""Pydantic 请求/响应模型。"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from hushai.meditation.core.skills import MAX_SKILLS_IMPORT_BATCH, MAX_SKILLS_PER_MESSAGE


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
    skill_ids: Optional[list[str]] = Field(default=None, max_length=MAX_SKILLS_PER_MESSAGE)
    provider: Optional[str] = None

    @field_validator("skill_ids", mode="before")
    @classmethod
    def _dedupe_skill_ids(cls, v: object) -> object:
        if v is None or not isinstance(v, list):
            return v
        seen: set[str] = set()
        out: list[str] = []
        for x in v:
            if not isinstance(x, str) or not x.strip():
                continue
            s = x.strip()
            if s in seen:
                continue
            seen.add(s)
            out.append(s)
            if len(out) >= MAX_SKILLS_PER_MESSAGE:
                break
        return out or None


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
    content_format: Literal["plain", "markdown"] = Field(
        default="plain",
        description="plain 按原文分块；markdown 解析 YAML 头与正文并转纯文本后入库，供 RAG 检索",
    )


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


class SkillPublicItem(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class SkillListResponse(BaseModel):
    skills: list[SkillPublicItem]


class SkillImportItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    content: str = Field(..., min_length=1)
    sort_order: int = 0
    is_active: bool = True

    @field_validator("name", "content", mode="before")
    @classmethod
    def strip_text(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("description", mode="before")
    @classmethod
    def strip_desc(cls, v: object) -> object:
        if v is None or v == "":
            return None
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


class SkillImportRequest(BaseModel):
    """JSON 可为 `{\"skills\": [...]}` 或顶层数组 `[...]`。"""

    skills: list[SkillImportItem] = Field(..., min_length=1, max_length=MAX_SKILLS_IMPORT_BATCH)

    @model_validator(mode="before")
    @classmethod
    def _accept_top_level_array(cls, data: Any) -> Any:
        if isinstance(data, list):
            return {"skills": data}
        return data


class SkillImportedRow(BaseModel):
    id: str
    name: str


class SkillImportResult(BaseModel):
    imported: int
    items: list[SkillImportedRow]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class StreamChunk(BaseModel):
    delta: str
    done: bool = False
    conversation_id: Optional[str] = None
