"""咨询师端管理 API。

提供咨询师入驻、排班管理、预约处理、服务记录编辑、收入统计等接口。
"""

import logging
from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.encryption import encrypt_field
from hushai.meditation.db.models import (
    Appointment,
    AppointmentSettings,
    AuditLog,
    ConsultationOrder,
    Counselor,
    CounselorSchedule,
    ServiceRecord,
)
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    AppointmentActionResponse,
    AppointmentItem,
    AppointmentListResponse,
    AppointmentSettingsResponse,
    AppointmentSettingsUpdate,
    CounselingStatsResponse,
    CounselorApplyRequest,
    CounselorDetailResponse,
    CounselorUpdateRequest,
    ScheduleListResponse,
    ScheduleSlotCreate,
    ScheduleSlotItem,
    ServiceRecordItem,
    ServiceRecordUpdateRequest,
)

logger = logging.getLogger("hushai.meditation.counselor_dashboard")

router = APIRouter(prefix="/api/counselor", tags=["counselor-dashboard"])


def _extract_token(authorization: str) -> str:
    return extract_bearer_token(authorization)


async def _require_user(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = _extract_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


async def _get_my_counselor(user_id: str, db: AsyncSession) -> Counselor:
    """获取当前用户关联的咨询师记录，未找到则 404。"""
    result = await db.execute(select(Counselor).where(Counselor.user_id == user_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="您尚未注册为咨询师")
    return c


# ── 入驻申请 ──


@router.post("/apply", response_model=CounselorDetailResponse)
async def apply_counselor(
    req: CounselorApplyRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """提交咨询师入驻申请。"""
    existing = await db.execute(select(Counselor).where(Counselor.user_id == user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="已提交过入驻申请")

    counselor = Counselor(
        user_id=user_id,
        real_name=req.real_name,
        phone=req.phone,
        email=req.email,
        specialties=req.specialties,
        certifications=req.certifications,
        bio=req.bio,
        hourly_rate=req.hourly_rate,
        status="pending",
    )
    db.add(counselor)
    await db.flush()
    await db.refresh(counselor)

    # 审计日志
    db.add(
        AuditLog(
            admin_username=user_id,
            action="counselor_apply",
            resource_type="counselor",
            resource_id=counselor.id,
            detail=f"提交入驻申请: {req.real_name}",
        )
    )
    await db.commit()

    return CounselorDetailResponse(
        id=counselor.id,
        real_name=counselor.real_name,
        specialties=counselor.specialties,
        certifications=counselor.certifications,
        bio=counselor.bio,
        hourly_rate=counselor.hourly_rate,
        is_online=counselor.is_online,
        status=counselor.status,
    )


# ── 个人资料 ──


@router.get("/profile", response_model=CounselorDetailResponse)
async def get_profile(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """查看咨询师个人资料。"""
    c = await _get_my_counselor(user_id, db)
    return CounselorDetailResponse(
        id=c.id,
        real_name=c.real_name,
        avatar_url=c.avatar_url,
        specialties=c.specialties,
        certifications=c.certifications,
        bio=c.bio,
        hourly_rate=c.hourly_rate,
        rating=c.rating,
        total_sessions=c.total_sessions,
        is_online=c.is_online,
        status=c.status,
    )


@router.put("/profile", response_model=CounselorDetailResponse)
async def update_profile(
    req: CounselorUpdateRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """编辑个人资料。"""
    c = await _get_my_counselor(user_id, db)
    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(c, k):
            setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return CounselorDetailResponse(
        id=c.id,
        real_name=c.real_name,
        avatar_url=c.avatar_url,
        specialties=c.specialties,
        certifications=c.certifications,
        bio=c.bio,
        hourly_rate=c.hourly_rate,
        rating=c.rating,
        total_sessions=c.total_sessions,
        is_online=c.is_online,
        status=c.status,
    )


# ── 排班管理 ──


@router.get("/schedule/manage", response_model=ScheduleListResponse)
async def list_my_schedule(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
    date_from: str | None = None,
    date_to: str | None = None,
):
    """查看我的排班。"""
    c = await _get_my_counselor(user_id, db)
    stmt = select(CounselorSchedule).where(CounselorSchedule.counselor_id == c.id)
    if date_from:
        stmt = stmt.where(CounselorSchedule.schedule_date >= date.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(CounselorSchedule.schedule_date <= date.fromisoformat(date_to))
    stmt = stmt.order_by(CounselorSchedule.schedule_date, CounselorSchedule.start_time)
    result = await db.execute(stmt)
    slots = result.scalars().all()
    return ScheduleListResponse(
        slots=[
            ScheduleSlotItem(
                id=s.id,
                schedule_date=s.schedule_date.isoformat(),
                start_time=s.start_time.strftime("%H:%M"),
                end_time=s.end_time.strftime("%H:%M"),
                slot_duration_minutes=s.slot_duration_minutes,
                max_bookings=s.max_bookings,
                is_available=s.is_available,
            )
            for s in slots
        ]
    )


@router.post("/schedule/manage", response_model=ScheduleSlotItem)
async def create_schedule_slot(
    req: ScheduleSlotCreate,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """创建排班时段。"""
    c = await _get_my_counselor(user_id, db)
    slot = CounselorSchedule(
        counselor_id=c.id,
        schedule_date=date.fromisoformat(req.schedule_date),
        start_time=time.fromisoformat(req.start_time),
        end_time=time.fromisoformat(req.end_time),
        slot_duration_minutes=req.slot_duration_minutes,
        max_bookings=req.max_bookings,
    )
    db.add(slot)
    await db.flush()
    await db.refresh(slot)
    await db.commit()
    return ScheduleSlotItem(
        id=slot.id,
        schedule_date=slot.schedule_date.isoformat(),
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
        slot_duration_minutes=slot.slot_duration_minutes,
        max_bookings=slot.max_bookings,
        is_available=slot.is_available,
    )


@router.delete("/schedule/manage/{slot_id}")
async def delete_schedule_slot(
    slot_id: str,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """删除排班时段（仅限未被预约的）。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(CounselorSchedule).where(
            CounselorSchedule.id == slot_id, CounselorSchedule.counselor_id == c.id
        )
    )
    slot = result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="排班不存在")

    # 检查是否已有预约
    appt_check = await db.execute(
        select(Appointment).where(
            Appointment.schedule_id == slot_id,
            Appointment.status.in_(["pending", "confirmed"]),
        )
    )
    if appt_check.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该时段已有预约，无法删除")

    await db.delete(slot)
    await db.commit()
    return {"success": True}


# ── 预约管理 ──


@router.get("/appointments/pending", response_model=AppointmentListResponse)
async def list_pending_appointments(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """待处理预约列表。"""
    c = await _get_my_counselor(user_id, db)
    stmt = (
        select(Appointment)
        .where(
            Appointment.counselor_id == c.id,
            Appointment.status == "pending",
        )
        .order_by(Appointment.appointment_date, Appointment.start_time)
    )
    result = await db.execute(stmt)
    appointments = result.scalars().all()

    items = [
        AppointmentItem(
            id=a.id,
            counselor_id=a.counselor_id,
            counselor_name=c.real_name,
            user_id=a.user_id,
            appointment_date=a.appointment_date.isoformat(),
            start_time=a.start_time.strftime("%H:%M"),
            end_time=a.end_time.strftime("%H:%M"),
            status=a.status,
            cancel_reason=a.cancel_reason,
            client_notes=a.client_notes,
            created_at=a.created_at,
        )
        for a in appointments
    ]
    return AppointmentListResponse(appointments=items, total=len(items))


@router.post("/appointments/{appointment_id}/confirm", response_model=AppointmentActionResponse)
async def confirm_appointment(
    appointment_id: str,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """确认预约。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id, Appointment.counselor_id == c.id
        )
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appt.status != "pending":
        raise HTTPException(status_code=400, detail="当前状态不可确认")

    appt.status = "confirmed"

    # 审计日志
    db.add(
        AuditLog(
            admin_username=user_id,
            action="appointment_confirm",
            resource_type="appointment",
            resource_id=appointment_id,
            detail=f"确认预约: {appt.appointment_date} {appt.start_time}",
        )
    )
    await db.commit()
    return AppointmentActionResponse(
        success=True, appointment_id=appointment_id, status="confirmed"
    )


@router.post("/appointments/{appointment_id}/reject", response_model=AppointmentActionResponse)
async def reject_appointment(
    appointment_id: str,
    reason: str | None = None,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """拒绝预约。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id, Appointment.counselor_id == c.id
        )
    )
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appt.status != "pending":
        raise HTTPException(status_code=400, detail="当前状态不可拒绝")

    appt.status = "rejected"
    appt.cancel_reason = reason

    db.add(
        AuditLog(
            admin_username=user_id,
            action="appointment_reject",
            resource_type="appointment",
            resource_id=appointment_id,
            detail=f"拒绝预约: {reason or '无原因'}",
        )
    )
    await db.commit()
    return AppointmentActionResponse(success=True, appointment_id=appointment_id, status="rejected")


# ── 服务记录 ──


@router.put("/service-records/{record_id}", response_model=ServiceRecordItem)
async def update_service_record(
    record_id: str,
    req: ServiceRecordUpdateRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """更新服务记录（咨询师填写咨询总结，敏感字段加密）。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(ServiceRecord).where(
            ServiceRecord.id == record_id, ServiceRecord.counselor_id == c.id
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="服务记录不存在")

    if req.service_type is not None:
        record.service_type = req.service_type
    if req.duration_minutes is not None:
        record.duration_minutes = req.duration_minutes
    if req.summary is not None:
        record.summary_encrypted = encrypt_field(req.summary)
    if req.counselor_notes is not None:
        record.counselor_notes_encrypted = encrypt_field(req.counselor_notes)
    if req.status is not None:
        record.status = req.status
        if req.status == "completed":
            record.ended_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)

    return ServiceRecordItem(
        id=record.id,
        order_id=record.order_id,
        appointment_id=record.appointment_id,
        counselor_id=record.counselor_id,
        counselor_name=c.real_name,
        user_id=record.user_id,
        service_type=record.service_type,
        duration_minutes=record.duration_minutes,
        status=record.status,
        started_at=record.started_at,
        ended_at=record.ended_at,
        created_at=record.created_at,
    )


# ── 预约配置 ──


@router.get("/settings", response_model=AppointmentSettingsResponse)
async def get_my_settings(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """获取我的预约配置。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(AppointmentSettings).where(AppointmentSettings.counselor_id == c.id)
    )
    s = result.scalar_one_or_none()
    if not s:
        # 返回全局默认配置
        global_result = await db.execute(
            select(AppointmentSettings).where(AppointmentSettings.counselor_id.is_(None))
        )
        s = global_result.scalar_one_or_none()
        if not s:
            raise HTTPException(status_code=404, detail="配置不存在")

    return AppointmentSettingsResponse(
        id=s.id,
        counselor_id=s.counselor_id,
        max_booking_count=s.max_booking_count,
        min_advance_hours=s.min_advance_hours,
        slot_duration_minutes=s.slot_duration_minutes,
        reminder_before_minutes=s.reminder_before_minutes,
        info_collection_enabled=s.info_collection_enabled,
        is_open=s.is_open,
    )


@router.put("/settings", response_model=AppointmentSettingsResponse)
async def update_my_settings(
    req: AppointmentSettingsUpdate,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """更新我的预约配置。"""
    c = await _get_my_counselor(user_id, db)
    result = await db.execute(
        select(AppointmentSettings).where(AppointmentSettings.counselor_id == c.id)
    )
    s = result.scalar_one_or_none()
    if not s:
        s = AppointmentSettings(counselor_id=c.id)
        db.add(s)

    update_data = req.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(s, k, v)

    await db.flush()
    await db.refresh(s)
    await db.commit()

    return AppointmentSettingsResponse(
        id=s.id,
        counselor_id=s.counselor_id,
        max_booking_count=s.max_booking_count,
        min_advance_hours=s.min_advance_hours,
        slot_duration_minutes=s.slot_duration_minutes,
        reminder_before_minutes=s.reminder_before_minutes,
        info_collection_enabled=s.info_collection_enabled,
        is_open=s.is_open,
    )


# ── 收入统计 ──


@router.get("/earnings/summary", response_model=CounselingStatsResponse)
async def earnings_summary(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """咨询师收入与统计概览。"""
    c = await _get_my_counselor(user_id, db)

    # 预约统计
    total_appt = (
        await db.execute(
            select(func.count()).select_from(Appointment).where(Appointment.counselor_id == c.id)
        )
    ).scalar() or 0
    pending_appt = (
        await db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.counselor_id == c.id, Appointment.status == "pending")
        )
    ).scalar() or 0
    completed_appt = (
        await db.execute(
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.counselor_id == c.id, Appointment.status == "completed")
        )
    ).scalar() or 0

    # 订单统计
    total_orders = (
        await db.execute(
            select(func.count())
            .select_from(ConsultationOrder)
            .where(ConsultationOrder.counselor_id == c.id)
        )
    ).scalar() or 0
    total_revenue = (
        await db.execute(
            select(func.coalesce(func.sum(ConsultationOrder.paid_amount), 0.0)).where(
                ConsultationOrder.counselor_id == c.id, ConsultationOrder.status == "paid"
            )
        )
    ).scalar() or 0.0

    return CounselingStatsResponse(
        total_appointments=total_appt,
        pending_appointments=pending_appt,
        completed_appointments=completed_appt,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_counselors=1,
        online_counselors=1 if c.is_online else 0,
    )
