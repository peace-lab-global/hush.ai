"""管理员 API 路由。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.memory import get_user_memories
from hushai.meditation.db.models import (
    Appointment,
    ConsultationOrder,
    Conversation,
    Counselor,
    Message,
    User,
)
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import CounselingStatsResponse, ErrorResponse, UserProfile

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _require_admin(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = extract_bearer_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.get(
    "/users/{user_id}/profile",
    response_model=UserProfile,
    responses={401: {"model": ErrorResponse}},
)
async def get_user_profile(
    user_id: str,
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
) -> UserProfile:
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    conv_count_stmt = (
        select(func.count()).select_from(Conversation).where(Conversation.user_id == user_id)
    )
    conv_count = (await session.execute(conv_count_stmt)).scalar() or 0
    msg_count_stmt = (
        select(func.count())
        .select_from(Message)
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == user_id)
    )
    msg_count = (await session.execute(msg_count_stmt)).scalar() or 0
    memories, _ = await get_user_memories(session, user_id, limit=100)
    memory_summary: dict[str, int] = {}
    for m in memories:
        memory_summary[m.category] = memory_summary.get(m.category, 0) + 1
    return UserProfile(
        user_id=user.id,
        nickname=user.nickname,
        created_at=user.created_at,
        total_conversations=conv_count,
        total_messages=msg_count,
        memory_summary=memory_summary,
    )


@router.get(
    "/users",
    responses={401: {"model": ErrorResponse}},
)
async def list_users(
    _admin: str = Depends(_require_admin),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> dict:
    stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    users = list(result.scalars().all())
    count_stmt = select(func.count()).select_from(User)
    total = (await session.execute(count_stmt)).scalar() or 0
    return {
        "users": [
            {
                "id": u.id,
                "nickname": u.nickname,
                "created_at": u.created_at.isoformat(),
                "is_active": u.is_active,
            }
            for u in users
        ],
        "total": total,
    }


# ──────────────────────────────────────────────────────────────────────────────
#  咨询服务管理 API
# ──────────────────────────────────────────────────────────────────────────────


class CounselorReviewRequest(BaseModel):
    action: str  # approve / reject
    reason: str | None = None


@router.get("/counseling/stats", response_model=CounselingStatsResponse)
async def counseling_stats(
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
):
    """咨询业务全局统计。"""
    total_appt = (
        await session.execute(select(func.count()).select_from(Appointment))
    ).scalar() or 0
    pending_appt = (
        await session.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "pending")
        )
    ).scalar() or 0
    completed_appt = (
        await session.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "completed")
        )
    ).scalar() or 0
    total_orders = (
        await session.execute(select(func.count()).select_from(ConsultationOrder))
    ).scalar() or 0
    total_revenue = (
        await session.execute(
            select(func.coalesce(func.sum(ConsultationOrder.paid_amount), 0.0)).where(
                ConsultationOrder.status == "paid"
            )
        )
    ).scalar() or 0.0
    total_counselors = (
        await session.execute(
            select(func.count()).select_from(Counselor).where(Counselor.status == "approved")
        )
    ).scalar() or 0
    online_counselors = (
        await session.execute(
            select(func.count())
            .select_from(Counselor)
            .where(Counselor.status == "approved", Counselor.is_online.is_(True))
        )
    ).scalar() or 0

    return CounselingStatsResponse(
        total_appointments=total_appt,
        pending_appointments=pending_appt,
        completed_appointments=completed_appt,
        total_orders=total_orders,
        total_revenue=float(total_revenue),
        total_counselors=total_counselors,
        online_counselors=online_counselors,
    )


@router.post("/counselors/{counselor_id}/review")
async def review_counselor(
    counselor_id: str,
    req: CounselorReviewRequest,
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
):
    """审核咨询师入驻申请。"""
    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    if req.action == "approve":
        c.status = "approved"
    elif req.action == "reject":
        c.status = "rejected"
    elif req.action == "disable":
        c.status = "disabled"
    else:
        raise HTTPException(status_code=400, detail="无效操作")

    from hushai.meditation.db.models import AuditLog

    session.add(
        AuditLog(
            admin_username=_admin,
            action=f"counselor_{req.action}",
            resource_type="counselor",
            resource_id=counselor_id,
            detail=f"审核操作: {req.action}, 原因: {req.reason or '无'}",
        )
    )
    await session.commit()
    return {"success": True, "counselor_id": counselor_id, "status": c.status}


@router.get("/counselors")
async def list_counselors_admin(
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """管理后台咨询师列表。"""
    stmt = select(Counselor).order_by(Counselor.created_at.desc()).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(Counselor.status == status)
    result = await session.execute(stmt)
    counselors = result.scalars().all()
    count_stmt = select(func.count()).select_from(Counselor)
    if status:
        count_stmt = count_stmt.where(Counselor.status == status)
    total = (await session.execute(count_stmt)).scalar() or 0

    return {
        "counselors": [
            {
                "id": c.id,
                "real_name": c.real_name,
                "phone": c.phone,
                "status": c.status,
                "is_online": c.is_online,
                "rating": c.rating,
                "total_sessions": c.total_sessions,
                "hourly_rate": c.hourly_rate,
                "created_at": c.created_at.isoformat(),
            }
            for c in counselors
        ],
        "total": total,
    }


@router.get("/orders")
async def list_orders_admin(
    _admin: str = Depends(_require_admin),
    session: AsyncSession = Depends(get_session),
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """管理后台订单列表。"""
    stmt = (
        select(ConsultationOrder)
        .order_by(ConsultationOrder.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status:
        stmt = stmt.where(ConsultationOrder.status == status)
    result = await session.execute(stmt)
    orders = result.scalars().all()
    count_stmt = select(func.count()).select_from(ConsultationOrder)
    if status:
        count_stmt = count_stmt.where(ConsultationOrder.status == status)
    total = (await session.execute(count_stmt)).scalar() or 0

    return {
        "orders": [
            {
                "id": o.id,
                "appointment_id": o.appointment_id,
                "counselor_id": o.counselor_id,
                "user_id": o.user_id,
                "order_type": o.order_type,
                "amount": o.amount,
                "paid_amount": o.paid_amount,
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            }
            for o in orders
        ],
        "total": total,
    }
