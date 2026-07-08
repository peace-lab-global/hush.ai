"""SQLAlchemy ORM 模型。"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    wx_openid: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True)
    wx_unionid: Mapped[Optional[str]] = mapped_column(String(128))
    wx_session_key: Mapped[Optional[str]] = mapped_column(String(256))
    nickname: Mapped[Optional[str]] = mapped_column(String(128))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    refresh_token_hash: Mapped[Optional[str]] = mapped_column(String(256), index=True)
    # refresh token 的 SHA-256 hex（非密钥），仅用于 O(1) 查找命中的用户，
    # 再用 refresh_token_hash 做最终校验。避免全表 bcrypt 扫描。
    refresh_token_selector: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, index=True
    )
    selected_teacher_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("teachers.id")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    conversations: Mapped[List[Conversation]] = relationship(back_populates="user")
    memories: Mapped[List[Memory]] = relationship(back_populates="user")
    meditation_sessions: Mapped[List["MeditationSession"]] = relationship(back_populates="user")
    daily_progress: Mapped[List["DailyProgress"]] = relationship(back_populates="user")
    selected_teacher: Mapped[Optional["Teacher"]] = relationship(foreign_keys=[selected_teacher_id])


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    user: Mapped[User] = relationship(back_populates="conversations")
    messages: Mapped[List[Message]] = relationship(back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    content: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(String(512))
    importance: Mapped[float] = mapped_column(Float, default=0.5)
    source_conversation_id: Mapped[Optional[str]] = mapped_column(ForeignKey("conversations.id"))
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    user: Mapped[User] = relationship(back_populates="memories")

    __table_args__ = (Index("ix_memories_user_category", "user_id", "category"),)


class Skill(Base):
    """可注入系统提示的「技能」片段，由管理后台维护，前台可多选加持。"""

    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(String(512))
    content: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[Optional[str]] = mapped_column(String(256))
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    parent_id: Mapped[Optional[str]] = mapped_column(ForeignKey("knowledge_chunks.id"), index=True)
    source: Mapped[Optional[str]] = mapped_column(String(256))
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)

    children: Mapped[List[KnowledgeChunk]] = relationship()


class Scene(Base):
    """冥想场景，用于区分不同应用场景的系统提示与引导策略。"""

    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128))
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    system_prompt: Mapped[str] = mapped_column(Text)
    opening_message: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class AdminUser(Base):
    """管理后台用户，支持多管理员账号。"""

    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    display_name: Mapped[Optional[str]] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class AuditLog(Base):
    """管理员操作审计日志。"""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    admin_username: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    resource_type: Mapped[str] = mapped_column(String(32))
    resource_id: Mapped[Optional[str]] = mapped_column(String(36))
    detail: Mapped[Optional[str]] = mapped_column(Text)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class MeditationSession(Base):
    """冥想会话记录。"""

    __tablename__ = "meditation_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(ForeignKey("conversations.id"))
    scene_id: Mapped[Optional[str]] = mapped_column(ForeignKey("scenes.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    mood_before: Mapped[Optional[int]] = mapped_column(Integer)
    mood_after: Mapped[Optional[int]] = mapped_column(Integer)
    note: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    user: Mapped[User] = relationship(back_populates="meditation_sessions")


class DailyProgress(Base):
    """用户每日进度统计。"""

    __tablename__ = "daily_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    meditation_count: Mapped[int] = mapped_column(Integer, default=0)
    total_duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    mood_avg: Mapped[Optional[float]] = mapped_column(Float)
    streak_day: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (Index("ix_daily_progress_user_date", "user_id", "date"),)

    user: Mapped[User] = relationship(back_populates="daily_progress")


class Teacher(Base):
    """冥想导师角色，不同导师有不同的引导风格和系统提示。"""

    __tablename__ = "teachers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(64))
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))
    avatar: Mapped[Optional[str]] = mapped_column(String(128))
    system_prompt: Mapped[str] = mapped_column(Text)
    default_voice: Mapped[Optional[str]] = mapped_column(String(128))
    voice_gender: Mapped[Optional[str]] = mapped_column(String(16))
    style_tags: Mapped[Optional[str]] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# ──────────────────────────────────────────────────────────────────────────────
#  咨询服务模型（心理咨询行业功能）
# ──────────────────────────────────────────────────────────────────────────────


class Counselor(Base):
    """心理咨询师。"""

    __tablename__ = "counselors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    real_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[Optional[str]] = mapped_column(String(32))
    email: Mapped[Optional[str]] = mapped_column(String(128))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    specialties: Mapped[Optional[list]] = mapped_column(JSON)
    certifications: Mapped[Optional[list]] = mapped_column(JSON)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / approved / rejected / disabled
    hourly_rate: Mapped[float] = mapped_column(Float, default=0.0)
    rating: Mapped[float] = mapped_column(Float, default=5.0)
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    schedules: Mapped[List["CounselorSchedule"]] = relationship(back_populates="counselor")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="counselor")


class CounselorSchedule(Base):
    """咨询师排班时段。"""

    __tablename__ = "counselor_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    schedule_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=50)
    max_bookings: Mapped[int] = mapped_column(Integer, default=1)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(back_populates="schedules")

    __table_args__ = (
        Index(
            "ix_counselor_schedule_unique",
            "counselor_id",
            "schedule_date",
            "start_time",
            unique=True,
        ),
    )


class Appointment(Base):
    """咨询预约。"""

    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    schedule_id: Mapped[Optional[str]] = mapped_column(ForeignKey("counselor_schedules.id"))
    appointment_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / confirmed / completed / cancelled / rejected
    cancel_reason: Mapped[Optional[str]] = mapped_column(Text)
    client_notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(back_populates="appointments")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    order: Mapped[Optional["ConsultationOrder"]] = relationship(back_populates="appointment")
    service_record: Mapped[Optional["ServiceRecord"]] = relationship(back_populates="appointment")


class ConsultationOrder(Base):
    """咨询订单。"""

    __tablename__ = "consultation_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    appointment_id: Mapped[str] = mapped_column(ForeignKey("appointments.id"), index=True)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    order_type: Mapped[str] = mapped_column(String(16), default="single")  # single / package
    package_name: Mapped[Optional[str]] = mapped_column(String(128))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(
        String(16), default="unpaid", index=True
    )  # unpaid / paid / refunded
    wx_transaction_id: Mapped[Optional[str]] = mapped_column(String(64))
    wx_prepay_id: Mapped[Optional[str]] = mapped_column(String(64))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    refunded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    appointment: Mapped["Appointment"] = relationship(back_populates="order")
    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    service_record: Mapped[Optional["ServiceRecord"]] = relationship(back_populates="order")


class ServiceRecord(Base):
    """咨询服务记录（敏感字段加密存储）。"""

    __tablename__ = "service_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("consultation_orders.id"), index=True
    )
    appointment_id: Mapped[Optional[str]] = mapped_column(ForeignKey("appointments.id"), index=True)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    service_type: Mapped[str] = mapped_column(String(32), default="standard")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    summary_encrypted: Mapped[Optional[str]] = mapped_column("summary", Text)
    counselor_notes_encrypted: Mapped[Optional[str]] = mapped_column("counselor_notes", Text)
    status: Mapped[str] = mapped_column(
        String(16), default="in_progress"
    )  # in_progress / completed / archived
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    order: Mapped[Optional["ConsultationOrder"]] = relationship(back_populates="service_record")
    appointment: Mapped[Optional["Appointment"]] = relationship(back_populates="service_record")
    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class AppointmentSettings(Base):
    """预约配置（全局或咨询师级别）。"""

    __tablename__ = "appointment_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("counselors.id"), unique=True, index=True
    )
    max_booking_count: Mapped[int] = mapped_column(Integer, default=5)
    min_advance_hours: Mapped[int] = mapped_column(Integer, default=2)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=50)
    reminder_before_minutes: Mapped[int] = mapped_column(Integer, default=5)
    info_collection_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped[Optional["Counselor"]] = relationship(foreign_keys=[counselor_id])
