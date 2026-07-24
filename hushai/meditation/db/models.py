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


# ──────────────────────────────────────────────────────────────────────────────
#  资质合规（P0）：证书、保险、合同、知情同意书
# ──────────────────────────────────────────────────────────────────────────────


class Credential(Base):
    """咨询师资质证书（结构化实体，区别于 Counselor.certifications 自由字符串）。

    记录发证机构、证书编号、有效期、证件附件与平台审核状态。
    """

    __tablename__ = "credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    credential_type: Mapped[str] = mapped_column(
        String(64), index=True
    )  # 如: 二级心理咨询师 / MBSR教师 /瑜伽教练 / 内观指导师
    issuing_body: Mapped[Optional[str]] = mapped_column(String(128))  # 发证机构
    credential_number: Mapped[Optional[str]] = mapped_column(String(128))  # 证书编号
    issued_at: Mapped[Optional[date]] = mapped_column(Date)
    expires_at: Mapped[Optional[date]] = mapped_column(Date, index=True)  # 到期日，用于提醒
    document_url: Mapped[Optional[str]] = mapped_column(String(512))  # 证件扫描件 URL
    scope: Mapped[Optional[str]] = mapped_column(String(256))  # 执业范围声明
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / verified / rejected / expired
    review_note: Mapped[Optional[str]] = mapped_column(Text)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    verified_by: Mapped[Optional[str]] = mapped_column(String(64))  # 审核管理员
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class Insurance(Base):
    """职业责任保险（malpractice / liability）。"""

    __tablename__ = "insurances"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    insurance_type: Mapped[str] = mapped_column(
        String(64), default="professional_liability"
    )  # professional_liability / public_liability
    carrier: Mapped[Optional[str]] = mapped_column(String(128))  # 承保公司
    policy_number: Mapped[Optional[str]] = mapped_column(String(128))
    coverage_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 保额
    coverage_start: Mapped[Optional[date]] = mapped_column(Date, index=True)
    coverage_end: Mapped[Optional[date]] = mapped_column(Date, index=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True
    )  # active / expired / lapsed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class CounselorContract(Base):
    """平台与咨询师的签约协议（版本化留档）。"""

    __tablename__ = "counselor_contracts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    contract_type: Mapped[str] = mapped_column(
        String(32), default="platform"
    )  # platform / eap / referral
    template_version: Mapped[Optional[str]] = mapped_column(String(32))
    commission_rate: Mapped[float] = mapped_column(
        Float, default=0.0
    )  # 平台抽佣比例 0.0-1.0
    effective_from: Mapped[Optional[date]] = mapped_column(Date)
    effective_until: Mapped[Optional[date]] = mapped_column(Date)
    document_url: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(
        String(16), default="draft", index=True
    )  # draft / active / terminated / expired
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    terminated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class InformedConsent(Base):
    """知情同意书（电子签署留档，法律合规要求）。"""

    __tablename__ = "informed_consents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("appointments.id"), index=True
    )
    consent_type: Mapped[str] = mapped_column(
        String(64), default="counseling"
    )  # counseling / data_processing / recording / minor_guardian
    template_version: Mapped[Optional[str]] = mapped_column(String(32))
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(128)
    )  # 同意书正文 SHA-256，用于日后举证比对
    is_agreed: Mapped[bool] = mapped_column(Boolean, default=False)
    agreed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


# ──────────────────────────────────────────────────────────────────────────────
#  收入与结算（P0）：钱包、结算单、提现、退款单、发票
# ──────────────────────────────────────────────────────────────────────────────


class CounselorWallet(Base):
    """咨询师资金钱包（可用余额、冻结、累计）。每个咨询师一行。"""

    __tablename__ = "counselor_wallets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(
        ForeignKey("counselors.id"), unique=True, index=True
    )
    available_balance: Mapped[float] = mapped_column(Float, default=0.0)  # 可提现
    pending_balance: Mapped[float] = mapped_column(Float, default=0.0)  # 冻结（未完成订单）
    withdrawn_total: Mapped[float] = mapped_column(Float, default=0.0)  # 累计已提现
    currency: Mapped[str] = mapped_column(String(8), default="CNY")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class Settlement(Base):
    """结算单：把已完成订单的收入计入咨询师钱包。"""

    __tablename__ = "settlements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    gross_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 订单总额
    platform_fee: Mapped[float] = mapped_column(Float, default=0.0)  # 平台抽佣
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 代扣税
    net_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 净结算额
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / settled / disputed
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    items: Mapped[List["SettlementItem"]] = relationship(back_populates="settlement")


class SettlementItem(Base):
    """结算单明细行（关联到具体订单）。"""

    __tablename__ = "settlement_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    settlement_id: Mapped[str] = mapped_column(ForeignKey("settlements.id"), index=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("consultation_orders.id"), index=True)
    gross_amount: Mapped[float] = mapped_column(Float, default=0.0)
    platform_fee: Mapped[float] = mapped_column(Float, default=0.0)
    net_amount: Mapped[float] = mapped_column(Float, default=0.0)

    settlement: Mapped["Settlement"] = relationship(back_populates="items")
    order: Mapped["ConsultationOrder"] = relationship()


class Payout(Base):
    """提现申请与处理记录。"""

    __tablename__ = "payouts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    fee: Mapped[float] = mapped_column(Float, default=0.0)  # 手续费
    method: Mapped[str] = mapped_column(
        String(32), default="bank"
    )  # bank / alipay / wechat
    destination: Mapped[Optional[str]] = mapped_column(
        String(256)
    )  # 银行卡号 / 支付宝账号（脱敏存储）
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / approved / paid / rejected
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    external_txn_id: Mapped[Optional[str]] = mapped_column(String(128))  # 银行/支付流水号
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class Refund(Base):
    """退款单（独立于 ConsultationOrder.status 的详细退款记录）。"""

    __tablename__ = "refunds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(ForeignKey("consultation_orders.id"), index=True)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    refund_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_order_amount: Mapped[float] = mapped_column(Float, default=0.0)
    reason: Mapped[Optional[str]] = mapped_column(String(256))
    initiator: Mapped[str] = mapped_column(
        String(16), default="user"
    )  # user / counselor / admin / system
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / approved / processing / succeeded / failed
    wx_refund_id: Mapped[Optional[str]] = mapped_column(String(64))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[Optional[str]] = mapped_column(String(64))
    succeeded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    order: Mapped["ConsultationOrder"] = relationship()
    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Invoice(Base):
    """发票（开票申请 + 税务信息）。"""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    invoice_no: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    payer_type: Mapped[str] = mapped_column(
        String(16), default="individual"
    )  # individual / corporate
    payer_name: Mapped[Optional[str]] = mapped_column(String(128))
    tax_id: Mapped[Optional[str]] = mapped_column(String(64))  # 税号（企业）
    invoice_type: Mapped[str] = mapped_column(
        String(32), default="general"
    )  # general / special / electronic
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    email: Mapped[Optional[str]] = mapped_column(String(128))  # 接收邮箱
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / issued / void
    issued_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    document_url: Mapped[Optional[str]] = mapped_column(String(512))
    related_order_ids: Mapped[Optional[list]] = mapped_column(JSON)  # 关联订单
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# ──────────────────────────────────────────────────────────────────────────────
#  客户与个案管理（P1）：客户档案、个案、治疗计划、入职问卷、危机标记
# ──────────────────────────────────────────────────────────────────────────────


class ClientProfile(Base):
    """咨询师视角的客户档案（个案聚合，独立于 User 通用账户）。

    同一个 User 对不同咨询师可以有多个 ClientProfile（一对多），
    便于咨询师维护自己的客户台账、诊断标签与风险等级。
    """

    __tablename__ = "client_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"), index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(128))  # 咨询师自定义备注名
    tags: Mapped[Optional[list]] = mapped_column(JSON)  # 诊断/议题标签
    risk_level: Mapped[str] = mapped_column(
        String(16), default="low", index=True
    )  # low / medium / high / crisis
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True
    )  # active / paused / closed / archived
    intake_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    first_session_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_session_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped[Optional["User"]] = relationship(foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_client_profile_counselor_user", "counselor_id", "user_id", unique=True),
    )


class TreatmentPlan(Base):
    """个案治疗/陪伴计划（目标、干预方案、进度）。"""

    __tablename__ = "treatment_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_profile_id: Mapped[str] = mapped_column(
        ForeignKey("client_profiles.id"), index=True
    )
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(256))
    presenting_issues: Mapped[Optional[str]] = mapped_column(Text)  # 主诉
    goals: Mapped[Optional[list]] = mapped_column(JSON)  # 目标列表
    interventions: Mapped[Optional[list]] = mapped_column(JSON)  # 干预手段
    modalities: Mapped[Optional[list]] = mapped_column(JSON)  # 流派：MBSR/MBCT/CBT/正念…
    estimated_sessions: Mapped[Optional[int]] = mapped_column(Integer)
    progress_notes_encrypted: Mapped[Optional[str]] = mapped_column(
        "progress_notes", Text
    )  # 进展记录（加密）
    outcome: Mapped[Optional[str]] = mapped_column(Text)  # 结案总结
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True
    )  # active / completed / discontinued
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    client_profile: Mapped["ClientProfile"] = relationship(foreign_keys=[client_profile_id])
    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    sessions: Mapped[List["SessionLog"]] = relationship(back_populates="plan")


class SessionLog(Base):
    """会谈记录（个案视角，补充 ServiceRecord 的订单视角）。

    一条记录关联一个治疗计划，追踪会谈序列与进展曲线。
    """

    __tablename__ = "session_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("treatment_plans.id"), index=True)
    client_profile_id: Mapped[str] = mapped_column(
        ForeignKey("client_profiles.id"), index=True
    )
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("appointments.id"), index=True
    )
    session_number: Mapped[Optional[int]] = mapped_column(Integer)  # 该个案第 N 次
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    modality: Mapped[Optional[str]] = mapped_column(
        String(32)
    )  # in_person / video / phone / chat
    summary_encrypted: Mapped[Optional[str]] = mapped_column("summary", Text)
    mood_before: Mapped[Optional[int]] = mapped_column(Integer)  # 1-10
    mood_after: Mapped[Optional[int]] = mapped_column(Integer)  # 1-10
    homework: Mapped[Optional[str]] = mapped_column(Text)  # 布置的练习作业
    status: Mapped[str] = mapped_column(
        String(16), default="completed"
    )  # scheduled / completed / no_show / cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    plan: Mapped["TreatmentPlan"] = relationship(back_populates="sessions")
    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class IntakeQuestionnaire(Base):
    """入职/接案问卷（结构化采集，由 AppointmentSettings.info_collection_enabled 触发）。"""

    __tablename__ = "intake_questionnaires"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_profile_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("client_profiles.id"), index=True
    )
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("appointments.id"), index=True
    )
    template_version: Mapped[Optional[str]] = mapped_column(String(32))
    responses: Mapped[Optional[dict]] = mapped_column(JSON)  # 问题-答案映射
    mood_baseline: Mapped[Optional[int]] = mapped_column(Integer)  # 初始情绪基线 1-10
    has_crisis_signals: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class CrisisFlag(Base):
    """危机个案标记与跟进（与 core/safety.py 危机检测打通）。"""

    __tablename__ = "crisis_flags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    client_profile_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("client_profiles.id"), index=True
    )
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    severity: Mapped[str] = mapped_column(
        String(16), default="moderate", index=True
    )  # mild / moderate / severe / imminent
    source: Mapped[str] = mapped_column(
        String(32), default="manual"
    )  # manual / safety_engine / intake
    description: Mapped[Optional[str]] = mapped_column(Text)
    action_taken: Mapped[Optional[str]] = mapped_column(Text)
    referred_to: Mapped[Optional[str]] = mapped_column(String(256))  # 转介机构
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Review(Base):
    """咨询评价（用户对咨询师，单次预约或整体）。"""

    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("appointments.id"), index=True
    )
    rating: Mapped[int] = mapped_column(Integer)  # 1-5
    communication_score: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5 分项
    professionalism_score: Mapped[Optional[int]] = mapped_column(Integer)
    effectiveness_score: Mapped[Optional[int]] = mapped_column(Integer)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSON)  # 正向标签
    counselor_reply: Mapped[Optional[str]] = mapped_column(Text)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)  # 疑似恶意/违规
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])

    __table_args__ = (
        Index("ix_reviews_counselor_published", "counselor_id", "is_published"),
    )


# ──────────────────────────────────────────────────────────────────────────────
#  学习成长（P2）：督导、继续教育、培训履历、个人练习
# ──────────────────────────────────────────────────────────────────────────────


class Supervision(Base):
    """督导记录（心理咨询/冥想引导行业的执业晋升硬性要求）。"""

    __tablename__ = "supervisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    supervisor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("counselors.id"), index=True
    )  # 督导师（也可是平台内咨询师）
    supervisor_name: Mapped[Optional[str]] = mapped_column(String(128))  # 外部督导师姓名
    supervision_type: Mapped[str] = mapped_column(
        String(32), default="individual"
    )  # individual / group / peer
    session_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    topics: Mapped[Optional[list]] = mapped_column(JSON)  # 议题/个案讨论
    notes_encrypted: Mapped[Optional[str]] = mapped_column("notes", Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(
        foreign_keys=[counselor_id]
    )
    supervisor: Mapped[Optional["Counselor"]] = relationship(foreign_keys=[supervisor_id])


class ContinuingEducation(Base):
    """继续教育学时（CEU，关系到续证）。"""

    __tablename__ = "continuing_education"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    course_name: Mapped[str] = mapped_column(String(256))
    provider: Mapped[Optional[str]] = mapped_column(String(256))  # 培训机构
    category: Mapped[str] = mapped_column(
        String(64), default="general", index=True
    )  # ethics / clinical / meditation / supervision / general
    completed_at: Mapped[Optional[date]] = mapped_column(Date)
    ceu_hours: Mapped[float] = mapped_column(Float, default=0.0)  # 学时
    certificate_url: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(
        String(16), default="completed"
    )  # enrolled / in_progress / completed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class TrainingRecord(Base):
    """培训履历（流派传承、项目经历）。"""

    __tablename__ = "training_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    program_name: Mapped[str] = mapped_column(String(256))
    tradition: Mapped[Optional[str]] = mapped_column(
        String(64)
    )  # MBSR / MBCT / 内观 / 禅修 / 藏传 / 道家 / 精神分析 …
    institution: Mapped[Optional[str]] = mapped_column(String(256))
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    level: Mapped[Optional[str]] = mapped_column(
        String(64)
    )  # 入门 / 初阶 / 中阶 / 高阶 / 教师认证
    certificate_url: Mapped[Optional[str]] = mapped_column(String(512))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class PersonalPractice(Base):
    """个人冥想/实修练习记录（冥想老师的隐性门槛）。"""

    __tablename__ = "personal_practices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    practice_type: Mapped[str] = mapped_column(
        String(64)
    )  # meditation / retreat / bodywork / personal_therapy
    practiced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    tradition: Mapped[Optional[str]] = mapped_column(String(64))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    is_retreat: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否闭关
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


# ──────────────────────────────────────────────────────────────────────────────
#  商业化扩展（P2）：内容/课程/工作坊/订阅/优惠券
# ──────────────────────────────────────────────────────────────────────────────


class Content(Base):
    """咨询师创作的内容（文章、音频、视频冥想引导）。

    与 KnowledgeChunk（RAG 语料）区分：这里是可以变现/公开展示的作者内容。
    """

    __tablename__ = "contents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    content_type: Mapped[str] = mapped_column(
        String(32), index=True
    )  # article / audio / video / meditation_script / ebook
    title: Mapped[str] = mapped_column(String(256))
    slug: Mapped[Optional[str]] = mapped_column(String(128), index=True)
    excerpt: Mapped[Optional[str]] = mapped_column(String(512))
    body: Mapped[Optional[str]] = mapped_column(Text)
    media_url: Mapped[Optional[str]] = mapped_column(String(512))
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))
    price: Mapped[float] = mapped_column(Float, default=0.0)  # 0=免费
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)  # 音视频时长
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class Course(Base):
    """系列课程（多课时）。"""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    subtitle: Mapped[Optional[str]] = mapped_column(String(512))
    description: Mapped[Optional[str]] = mapped_column(Text)
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))
    price: Mapped[float] = mapped_column(Float, default=0.0)
    original_price: Mapped[Optional[float]] = mapped_column(Float)
    format: Mapped[str] = mapped_column(
        String(32), default="self_paced"
    )  # self_paced / cohort / live
    total_lessons: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[Optional[str]] = mapped_column(String(32))  # 入门 / 进阶 / 教师
    category: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    enroll_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course")


class Lesson(Base):
    """课程课时。"""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    content_type: Mapped[str] = mapped_column(
        String(32), default="video"
    )  # video / audio / text / live
    media_url: Mapped[Optional[str]] = mapped_column(String(512))
    body: Mapped[Optional[str]] = mapped_column(Text)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_preview: Mapped[bool] = mapped_column(Boolean, default=False)  # 免费试看
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    course: Mapped["Course"] = relationship(back_populates="lessons")


class Workshop(Base):
    """工作坊/团体活动（一次性或短期集体活动）。"""

    __tablename__ = "workshops"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text)
    format: Mapped[str] = mapped_column(
        String(32), default="online"
    )  # online / in_person / hybrid
    location: Mapped[Optional[str]] = mapped_column(String(256))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    max_participants: Mapped[Optional[int]] = mapped_column(Integer)
    enrolled_count: Mapped[int] = mapped_column(Integer, default=0)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(
        String(16), default="open", index=True
    )  # open / full / closed / completed / cancelled
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])


class Subscription(Base):
    """会员订阅（月度陪伴、unlimited 等）。"""

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(ForeignKey("counselors.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    plan_name: Mapped[str] = mapped_column(String(128))
    billing_cycle: Mapped[str] = mapped_column(
        String(16), default="monthly"
    )  # monthly / quarterly / yearly
    price: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True
    )  # active / paused / cancelled / expired
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class Coupon(Base):
    """优惠券/促销码。"""

    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    coupon_type: Mapped[str] = mapped_column(
        String(16), default="discount"
    )  # discount / amount / trial
    discount_value: Mapped[float] = mapped_column(
        Float, default=0.0
    )  # 百分比(0-100) 或固定金额
    min_amount: Mapped[float] = mapped_column(Float, default=0.0)  # 满减门槛
    max_uses: Mapped[Optional[int]] = mapped_column(Integer)  # 总发放量
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    max_uses_per_user: Mapped[int] = mapped_column(Integer, default=1)
    applies_to: Mapped[str] = mapped_column(
        String(32), default="all"
    )  # all / appointment / course / workshop / subscription
    counselor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("counselors.id"), index=True
    )  # null=全平台
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    counselor: Mapped[Optional["Counselor"]] = relationship(foreign_keys=[counselor_id])


# ──────────────────────────────────────────────────────────────────────────────
#  生态扩展（P3）：转介、企业 EAP、视频会谈、外部日历同步
# ──────────────────────────────────────────────────────────────────────────────


class Referral(Base):
    """转介记录（咨询师间转介 / 转介给外部机构）。"""

    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    from_counselor_id: Mapped[str] = mapped_column(
        ForeignKey("counselors.id"), index=True
    )
    to_counselor_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("counselors.id"), index=True
    )  # 平台内接收方（可为空表示外部转介）
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    external_target: Mapped[Optional[str]] = mapped_column(
        String(256)
    )  # 外部机构名称（外部转介时填写）
    reason: Mapped[Optional[str]] = mapped_column(Text)
    match_criteria: Mapped[Optional[list]] = mapped_column(JSON)  # 匹配维度
    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending / accepted / declined / completed
    referred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    from_counselor: Mapped["Counselor"] = relationship(foreign_keys=[from_counselor_id])
    to_counselor: Mapped[Optional["Counselor"]] = relationship(foreign_keys=[to_counselor_id])
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class EnterpriseAccount(Base):
    """企业 EAP 账户（对公客户）。"""

    __tablename__ = "enterprise_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_name: Mapped[str] = mapped_column(String(256), index=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(128))
    contact_email: Mapped[Optional[str]] = mapped_column(String(128))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(32))
    contract_value: Mapped[float] = mapped_column(Float, default=0.0)
    employee_quota: Mapped[int] = mapped_column(Integer, default=0)  # 员工名额
    used_quota: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(16), default="active", index=True
    )  # active / suspended / expired
    effective_from: Mapped[Optional[date]] = mapped_column(Date)
    effective_until: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class VideoSession(Base):
    """视频会谈（远程咨询的会议链接与状态）。"""

    __tablename__ = "video_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    appointment_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("appointments.id"), unique=True, index=True
    )
    provider: Mapped[str] = mapped_column(
        String(32), default="internal"
    )  # internal / zoom / tencent / agora
    room_id: Mapped[Optional[str]] = mapped_column(String(128))
    host_url: Mapped[Optional[str]] = mapped_column(String(512))
    guest_url: Mapped[Optional[str]] = mapped_column(String(512))
    join_token: Mapped[Optional[str]] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(
        String(16), default="scheduled"
    )  # scheduled / live / ended / failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    recording_url: Mapped[Optional[str]] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


class CalendarSync(Base):
    """外部日历同步配置（避免双重预订）。"""

    __tablename__ = "calendar_syncs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    counselor_id: Mapped[str] = mapped_column(
        ForeignKey("counselors.id"), unique=True, index=True
    )
    provider: Mapped[str] = mapped_column(
        String(32)
    )  # google / outlook / ical / apple
    external_calendar_id: Mapped[Optional[str]] = mapped_column(String(256))
    ical_feed_url: Mapped[Optional[str]] = mapped_column(String(512))
    sync_direction: Mapped[str] = mapped_column(
        String(16), default="two_way"
    )  # import_only / export_only / two_way
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    counselor: Mapped["Counselor"] = relationship(foreign_keys=[counselor_id])
