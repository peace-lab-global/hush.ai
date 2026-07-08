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
    scene_id: Optional[str] = None
    teacher_id: Optional[str] = None

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


class KnowledgeSourceItem(BaseModel):
    id: str | None = None
    title: str | None = None
    score: float = 0.0


class KnowledgeQAResponse(BaseModel):
    reply: str
    conversation_id: str
    sources: list[KnowledgeSourceItem] = []


class WxLoginRequest(BaseModel):
    code: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    nickname: Optional[str] = None
    expires_in: int = 604800


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 604800


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


class RemoteImportRequest(BaseModel):
    """远程知识源导入请求。"""

    source_type: Literal["url", "coze", "ima"] = "url"
    urls: Optional[list[str]] = Field(
        default=None, description="URL 列表（source_type=url/ima 时使用）"
    )
    config: dict[str, Any] = Field(
        default_factory=dict, description="源配置 (api_token, dataset_id 等)"
    )
    tags: list[str] = Field(default_factory=list)


class RemoteImportResult(BaseModel):
    imported: int
    results: list[dict[str, Any]]
    errors: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class StreamChunk(BaseModel):
    delta: str
    done: bool = False
    conversation_id: Optional[str] = None


class ScenePublicItem(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    opening_message: Optional[str] = None


class SceneListResponse(BaseModel):
    scenes: list[ScenePublicItem]


# ──────────────────────────────────────────────────────────────────────────────
#  咨询服务 Pydantic 模型
# ──────────────────────────────────────────────────────────────────────────────


class CounselorStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISABLED = "disabled"


class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class ServiceRecordStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# ── 咨询师 ──


class CounselorItem(BaseModel):
    id: str
    real_name: str
    avatar_url: Optional[str] = None
    specialties: Optional[list] = None
    bio: Optional[str] = None
    hourly_rate: float = 0.0
    rating: float = 5.0
    total_sessions: int = 0
    is_online: bool = False


class CounselorListResponse(BaseModel):
    counselors: list[CounselorItem]
    total: int


class CounselorDetailResponse(BaseModel):
    id: str
    real_name: str
    avatar_url: Optional[str] = None
    specialties: Optional[list] = None
    certifications: Optional[list] = None
    bio: Optional[str] = None
    hourly_rate: float = 0.0
    rating: float = 5.0
    total_sessions: int = 0
    is_online: bool = False
    status: str


class CounselorApplyRequest(BaseModel):
    real_name: str = Field(..., min_length=1, max_length=64)
    phone: Optional[str] = Field(None, max_length=32)
    email: Optional[str] = Field(None, max_length=128)
    specialties: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    bio: Optional[str] = None
    hourly_rate: float = Field(0.0, ge=0)


class CounselorUpdateRequest(BaseModel):
    real_name: Optional[str] = Field(None, max_length=64)
    phone: Optional[str] = Field(None, max_length=32)
    email: Optional[str] = Field(None, max_length=128)
    avatar_url: Optional[str] = Field(None, max_length=512)
    specialties: Optional[list[str]] = None
    certifications: Optional[list[str]] = None
    bio: Optional[str] = None
    hourly_rate: Optional[float] = Field(None, ge=0)
    is_online: Optional[bool] = None


# ── 排班 ──


class ScheduleSlotCreate(BaseModel):
    schedule_date: str = Field(..., description="YYYY-MM-DD")
    start_time: str = Field(..., description="HH:MM")
    end_time: str = Field(..., description="HH:MM")
    slot_duration_minutes: int = 50
    max_bookings: int = 1


class ScheduleSlotItem(BaseModel):
    id: str
    schedule_date: str
    start_time: str
    end_time: str
    slot_duration_minutes: int
    max_bookings: int
    is_available: bool


class ScheduleListResponse(BaseModel):
    slots: list[ScheduleSlotItem]


# ── 预约 ──


class AppointmentCreateRequest(BaseModel):
    counselor_id: str
    schedule_id: Optional[str] = None
    appointment_date: str = Field(..., description="YYYY-MM-DD")
    start_time: str = Field(..., description="HH:MM")
    end_time: str = Field(..., description="HH:MM")
    client_notes: Optional[str] = None


class AppointmentItem(BaseModel):
    id: str
    counselor_id: str
    counselor_name: Optional[str] = None
    user_id: str
    appointment_date: str
    start_time: str
    end_time: str
    status: str
    cancel_reason: Optional[str] = None
    client_notes: Optional[str] = None
    created_at: datetime


class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentItem]
    total: int


class AppointmentCancelRequest(BaseModel):
    cancel_reason: Optional[str] = None


class AppointmentActionResponse(BaseModel):
    success: bool
    appointment_id: str
    status: str


# ── 订单 ──


class OrderCreateRequest(BaseModel):
    appointment_id: str
    order_type: Literal["single", "package"] = "single"
    package_name: Optional[str] = None
    amount: float = Field(..., ge=0)


class OrderItem(BaseModel):
    id: str
    appointment_id: str
    counselor_id: str
    counselor_name: Optional[str] = None
    user_id: str
    order_type: str
    package_name: Optional[str] = None
    amount: float
    paid_amount: float
    status: str
    created_at: datetime
    paid_at: Optional[datetime] = None


class OrderListResponse(BaseModel):
    orders: list[OrderItem]
    total: int


class OrderDetailResponse(BaseModel):
    id: str
    appointment_id: str
    counselor_id: str
    counselor_name: Optional[str] = None
    user_id: str
    order_type: str
    package_name: Optional[str] = None
    amount: float
    paid_amount: float
    status: str
    wx_transaction_id: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None


class PayRequest(BaseModel):
    order_id: str
    pay_method: Literal["native", "jsapi"] = "native"


class PayResponse(BaseModel):
    order_id: str
    code_url: Optional[str] = None
    prepay_id: Optional[str] = None
    status: str


# ── 服务记录 ──


class ServiceRecordUpdateRequest(BaseModel):
    service_type: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    summary: Optional[str] = None
    counselor_notes: Optional[str] = None
    status: Optional[Literal["in_progress", "completed", "archived"]] = None


class ServiceRecordItem(BaseModel):
    id: str
    order_id: Optional[str] = None
    appointment_id: Optional[str] = None
    counselor_id: str
    counselor_name: Optional[str] = None
    user_id: str
    service_type: str
    duration_minutes: int
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime


class ServiceRecordListResponse(BaseModel):
    records: list[ServiceRecordItem]
    total: int


# ── 预约配置 ──


class AppointmentSettingsUpdate(BaseModel):
    max_booking_count: Optional[int] = Field(None, ge=1, le=20)
    min_advance_hours: Optional[int] = Field(None, ge=0, le=168)
    slot_duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    reminder_before_minutes: Optional[int] = Field(None, ge=0, le=60)
    info_collection_enabled: Optional[bool] = None
    is_open: Optional[bool] = None


class AppointmentSettingsResponse(BaseModel):
    id: str
    counselor_id: Optional[str] = None
    max_booking_count: int
    min_advance_hours: int
    slot_duration_minutes: int
    reminder_before_minutes: int
    info_collection_enabled: bool
    is_open: bool


# ── 统计 ──


class CounselingStatsResponse(BaseModel):
    total_appointments: int
    pending_appointments: int
    completed_appointments: int
    total_orders: int
    total_revenue: float
    total_counselors: int
    online_counselors: int
