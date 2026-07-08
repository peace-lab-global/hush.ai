"""预约管理页面。"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.db.models import Appointment, Counselor, User

router = APIRouter(tags=["admin-web"])


@router.get("/appointments", response_class=HTMLResponse)
async def appointments_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    counselor_name: str = "",
    date_from: str = "",
    date_to: str = "",
    session: AsyncSession = Depends(get_session),
):
    """预约管理列表页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit
    base_query = select(Appointment)
    count_query = select(func.count()).select_from(Appointment)

    if status:
        base_query = base_query.where(Appointment.status == status)
        count_query = count_query.where(Appointment.status == status)
    if date_from:
        d = date.fromisoformat(date_from)
        base_query = base_query.where(Appointment.appointment_date >= d)
        count_query = count_query.where(Appointment.appointment_date >= d)
    if date_to:
        d = date.fromisoformat(date_to)
        base_query = base_query.where(Appointment.appointment_date <= d)
        count_query = count_query.where(Appointment.appointment_date <= d)

    result = await session.execute(
        base_query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
        .offset(offset)
        .limit(limit)
    )
    appointments = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if limit else 1

    # 统计数据
    stats = {
        "total": total,
        "pending": (
            await session.execute(
                select(func.count()).select_from(Appointment).where(Appointment.status == "pending")
            )
        ).scalar()
        or 0,
        "confirmed": (
            await session.execute(
                select(func.count())
                .select_from(Appointment)
                .where(Appointment.status == "confirmed")
            )
        ).scalar()
        or 0,
        "completed": (
            await session.execute(
                select(func.count())
                .select_from(Appointment)
                .where(Appointment.status == "completed")
            )
        ).scalar()
        or 0,
        "cancelled": (
            await session.execute(
                select(func.count())
                .select_from(Appointment)
                .where(Appointment.status == "cancelled")
            )
        ).scalar()
        or 0,
    }

    return templates.TemplateResponse(
        request,
        "appointments.html",
        {
            "admin_user": admin_user,
            "appointments": appointments,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "status_filter": status,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit,
            "stats": stats,
        },
    )


@router.get("/appointments/{appointment_id}", response_class=HTMLResponse)
async def appointment_detail_page(
    request: Request,
    appointment_id: str,
    session: AsyncSession = Depends(get_session),
):
    """预约详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = result.scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="预约不存在")

    # 获取咨询师和用户信息
    c_result = await session.execute(select(Counselor).where(Counselor.id == appt.counselor_id))
    counselor = c_result.scalar_one_or_none()
    u_result = await session.execute(select(User).where(User.id == appt.user_id))
    user = u_result.scalar_one_or_none()

    return templates.TemplateResponse(
        request,
        "appointment_detail.html",
        {
            "admin_user": admin_user,
            "appointment": appt,
            "counselor": counselor,
            "user": user,
        },
    )
