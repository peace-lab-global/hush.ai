"""订单管理页面。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import get_session, login_redirect, templates
from hushai.meditation.db.models import ConsultationOrder, Counselor, User

router = APIRouter(tags=["admin-web"])


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    session: AsyncSession = Depends(get_session),
):
    """订单管理列表页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    offset = (page - 1) * limit
    base_query = select(ConsultationOrder)
    count_query = select(func.count()).select_from(ConsultationOrder)

    if status:
        base_query = base_query.where(ConsultationOrder.status == status)
        count_query = count_query.where(ConsultationOrder.status == status)

    result = await session.execute(
        base_query.order_by(ConsultationOrder.created_at.desc()).offset(offset).limit(limit)
    )
    orders = list(result.scalars().all())
    total = (await session.execute(count_query)).scalar() or 0
    total_pages = (total + limit - 1) // limit if limit else 1

    # 金额统计
    total_revenue = (
        await session.execute(
            select(func.coalesce(func.sum(ConsultationOrder.paid_amount), 0.0)).where(
                ConsultationOrder.status == "paid"
            )
        )
    ).scalar() or 0.0
    total_amount = (
        await session.execute(select(func.coalesce(func.sum(ConsultationOrder.amount), 0.0)))
    ).scalar() or 0.0

    stats = {
        "total_orders": total,
        "unpaid": (
            await session.execute(
                select(func.count())
                .select_from(ConsultationOrder)
                .where(ConsultationOrder.status == "unpaid")
            )
        ).scalar()
        or 0,
        "paid": (
            await session.execute(
                select(func.count())
                .select_from(ConsultationOrder)
                .where(ConsultationOrder.status == "paid")
            )
        ).scalar()
        or 0,
        "refunded": (
            await session.execute(
                select(func.count())
                .select_from(ConsultationOrder)
                .where(ConsultationOrder.status == "refunded")
            )
        ).scalar()
        or 0,
        "total_revenue": float(total_revenue),
        "total_amount": float(total_amount),
    }

    return templates.TemplateResponse(
        request,
        "orders.html",
        {
            "admin_user": admin_user,
            "orders": orders,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "status_filter": status,
            "limit": limit,
            "stats": stats,
        },
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
async def order_detail_page(
    request: Request,
    order_id: str,
    session: AsyncSession = Depends(get_session),
):
    """订单详情页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    result = await session.execute(
        select(ConsultationOrder).where(ConsultationOrder.id == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    c_result = await session.execute(select(Counselor).where(Counselor.id == order.counselor_id))
    counselor = c_result.scalar_one_or_none()
    u_result = await session.execute(select(User).where(User.id == order.user_id))
    user = u_result.scalar_one_or_none()

    return templates.TemplateResponse(
        request,
        "order_detail.html",
        {
            "admin_user": admin_user,
            "order": order,
            "counselor": counselor,
            "user": user,
        },
    )
