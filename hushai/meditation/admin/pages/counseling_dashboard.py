"""咨询数据看板页面。"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.db.models import (
    Appointment,
    ConsultationOrder,
    Counselor,
    ServiceRecord,
)

router = APIRouter(tags=["admin-web"])


@router.get("/counseling-dashboard", response_class=HTMLResponse)
async def counseling_dashboard_page(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """咨询数据看板页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    # ── 咨询师统计 ──
    total_counselors = (
        await session.execute(select(func.count()).select_from(Counselor))
    ).scalar() or 0
    approved_counselors = (
        await session.execute(
            select(func.count()).select_from(Counselor).where(Counselor.status == "approved")
        )
    ).scalar() or 0
    pending_counselors = (
        await session.execute(
            select(func.count()).select_from(Counselor).where(Counselor.status == "pending")
        )
    ).scalar() or 0
    online_counselors = (
        await session.execute(
            select(func.count())
            .select_from(Counselor)
            .where(Counselor.status == "approved", Counselor.is_online.is_(True))
        )
    ).scalar() or 0

    # ── 预约统计 ──
    total_appointments = (
        await session.execute(select(func.count()).select_from(Appointment))
    ).scalar() or 0
    pending_appointments = (
        await session.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "pending")
        )
    ).scalar() or 0
    confirmed_appointments = (
        await session.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "confirmed")
        )
    ).scalar() or 0
    completed_appointments = (
        await session.execute(
            select(func.count()).select_from(Appointment).where(Appointment.status == "completed")
        )
    ).scalar() or 0

    # ── 订单统计 ──
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
    today = date.today()
    today_orders = (
        await session.execute(
            select(func.count())
            .select_from(ConsultationOrder)
            .where(func.date(ConsultationOrder.created_at) == today)
        )
    ).scalar() or 0

    # ── 服务记录统计 ──
    total_service_records = (
        await session.execute(select(func.count()).select_from(ServiceRecord))
    ).scalar() or 0
    total_service_hours = (
        await session.execute(
            select(func.coalesce(func.sum(ServiceRecord.duration_minutes), 0)).where(
                ServiceRecord.status == "completed"
            )
        )
    ).scalar() or 0

    # ── 最近待审核咨询师 ──
    pending_review = (
        (
            await session.execute(
                select(Counselor)
                .where(Counselor.status == "pending")
                .order_by(Counselor.created_at.desc())
                .limit(5)
            )
        )
        .scalars()
        .all()
    )

    # ── 今日预约 ──
    today_appointments = (
        (
            await session.execute(
                select(Appointment)
                .where(Appointment.appointment_date == today)
                .order_by(Appointment.start_time)
                .limit(10)
            )
        )
        .scalars()
        .all()
    )

    return templates.TemplateResponse(
        request,
        "counseling_dashboard.html",
        {
            "admin_user": admin_user,
            "stats": {
                "total_counselors": total_counselors,
                "approved_counselors": approved_counselors,
                "pending_counselors": pending_counselors,
                "online_counselors": online_counselors,
                "total_appointments": total_appointments,
                "pending_appointments": pending_appointments,
                "confirmed_appointments": confirmed_appointments,
                "completed_appointments": completed_appointments,
                "total_orders": total_orders,
                "total_revenue": float(total_revenue),
                "today_orders": today_orders,
                "total_service_records": total_service_records,
                "total_service_hours": total_service_hours // 60,
            },
            "pending_review": pending_review,
            "today_appointments": today_appointments,
            "today": today,
        },
    )
