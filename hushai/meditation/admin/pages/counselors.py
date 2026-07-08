"""咨询师管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.core.encryption import mask_phone
from hushai.meditation.db.models import (
    Appointment,
    AuditLog,
    Counselor,
    CounselorSchedule,
)

router = APIRouter(tags=["admin-web"])


@router.get("/counselors", response_class=HTMLResponse)
async def counselors_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    search: str = "",
    session: AsyncSession = Depends(get_session),
):
    """咨询师列表页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit
    base_query = select(Counselor)
    count_query = select(func.count()).select_from(Counselor)

    if status:
        base_query = base_query.where(Counselor.status == status)
        count_query = count_query.where(Counselor.status == status)
    if search:
        base_query = base_query.where(
            (Counselor.real_name.ilike(f"%{search}%")) | (Counselor.phone.ilike(f"%{search}%"))
        )
        count_query = count_query.where(
            (Counselor.real_name.ilike(f"%{search}%")) | (Counselor.phone.ilike(f"%{search}%"))
        )

    result = await session.execute(
        base_query.order_by(Counselor.created_at.desc()).offset(offset).limit(limit)
    )
    counselors = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if limit else 1

    # 统计数据
    stats = {
        "total": total,
        "pending": (
            await session.execute(
                select(func.count()).select_from(Counselor).where(Counselor.status == "pending")
            )
        ).scalar()
        or 0,
        "approved": (
            await session.execute(
                select(func.count()).select_from(Counselor).where(Counselor.status == "approved")
            )
        ).scalar()
        or 0,
        "online": (
            await session.execute(
                select(func.count())
                .select_from(Counselor)
                .where(Counselor.status == "approved", Counselor.is_online.is_(True))
            )
        ).scalar()
        or 0,
    }

    return templates.TemplateResponse(
        request,
        "counselors.html",
        {
            "admin_user": admin_user,
            "counselors": counselors,
            "mask_phone": mask_phone,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "search": search,
            "status_filter": status,
            "limit": limit,
            "stats": stats,
        },
    )


@router.get("/counselors/{counselor_id}", response_class=HTMLResponse)
async def counselor_detail_page(
    request: Request,
    counselor_id: str,
    session: AsyncSession = Depends(get_session),
):
    """咨询师详情/审核页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    counselor = result.scalar_one_or_none()
    if not counselor:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    # 排班统计
    schedule_count = (
        await session.execute(
            select(func.count())
            .select_from(CounselorSchedule)
            .where(CounselorSchedule.counselor_id == counselor_id)
        )
    ).scalar() or 0

    # 预约统计
    appt_count = (
        await session.execute(
            select(func.count())
            .select_from(Appointment)
            .where(Appointment.counselor_id == counselor_id)
        )
    ).scalar() or 0
    pending_appt = (
        await session.execute(
            select(func.count())
            .select_from(Appointment)
            .where(
                Appointment.counselor_id == counselor_id,
                Appointment.status == "pending",
            )
        )
    ).scalar() or 0

    return templates.TemplateResponse(
        request,
        "counselor_detail.html",
        {
            "admin_user": admin_user,
            "counselor": counselor,
            "mask_phone": mask_phone,
            "schedule_count": schedule_count,
            "appt_count": appt_count,
            "pending_appt": pending_appt,
        },
    )


@router.post("/counselors/{counselor_id}/review")
async def review_counselor_page(
    request: Request,
    counselor_id: str,
    action: str,
    reason: str = "",
    session: AsyncSession = Depends(get_session),
):
    """审核咨询师（页面端 API）。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    if action == "approve":
        c.status = "approved"
    elif action == "reject":
        c.status = "rejected"
    elif action == "disable":
        c.status = "disabled"
    else:
        raise HTTPException(status_code=400, detail="无效操作")

    session.add(
        AuditLog(
            admin_username=admin_user,
            action=f"counselor_{action}",
            resource_type="counselor",
            resource_id=counselor_id,
            detail=f"审核操作: {action}, 原因: {reason or '无'}",
        )
    )
    await session.commit()
    return {"success": True, "status": c.status}


@router.post("/counselors/{counselor_id}/toggle-online")
async def toggle_counselor_online(
    request: Request,
    counselor_id: str,
    session: AsyncSession = Depends(get_session),
):
    """切换咨询师上线状态。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        raise HTTPException(status_code=401, detail="需要管理员登录")

    result = await session.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="咨询师不存在")

    c.is_online = not c.is_online
    await session.commit()
    return {"success": True, "is_online": c.is_online}
