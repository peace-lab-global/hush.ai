"""用户端心理咨询 API。

提供咨询师浏览、预约、订单、支付、服务记录等接口。
"""

import logging
from datetime import date, datetime, time, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core import wechat_pay
from hushai.meditation.db.models import (
    Appointment,
    AppointmentSettings,
    ConsultationOrder,
    Counselor,
    CounselorSchedule,
    ServiceRecord,
)
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    AppointmentCancelRequest,
    AppointmentCreateRequest,
    AppointmentItem,
    AppointmentListResponse,
    CounselorDetailResponse,
    CounselorItem,
    CounselorListResponse,
    OrderCreateRequest,
    OrderDetailResponse,
    OrderItem,
    OrderListResponse,
    PayRequest,
    PayResponse,
    ScheduleListResponse,
    ScheduleSlotItem,
    ServiceRecordItem,
    ServiceRecordListResponse,
)

logger = logging.getLogger("hushai.meditation.counseling")

router = APIRouter(prefix="/api/counseling", tags=["counseling"])


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


# ── 咨询师浏览 ──


@router.get("/counselors/list", response_model=CounselorListResponse)
async def list_counselors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    specialty: str | None = None,
    db: AsyncSession = Depends(get_session),
    _user_id: str = Depends(_require_user),
):
    """已认证的咨询师列表（支持分页和领域筛选）。"""
    stmt = select(Counselor).where(Counselor.status == "approved", Counselor.is_online.is_(True))
    if specialty:
        stmt = stmt.where(Counselor.specialties.contains([specialty]))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Counselor.sort_order.asc(), Counselor.rating.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    counselors = result.scalars().all()

    return CounselorListResponse(
        total=total,
        counselors=[
            CounselorItem(
                id=c.id,
                real_name=c.real_name,
                avatar_url=c.avatar_url,
                specialties=c.specialties,
                bio=c.bio,
                hourly_rate=c.hourly_rate,
                rating=c.rating,
                total_sessions=c.total_sessions,
                is_online=c.is_online,
            )
            for c in counselors
        ],
    )


@router.get("/counselors/{counselor_id}", response_model=CounselorDetailResponse)
async def get_counselor(
    counselor_id: str,
    db: AsyncSession = Depends(get_session),
    _user_id: str = Depends(_require_user),
):
    """咨询师详情（名片）。"""
    result = await db.execute(select(Counselor).where(Counselor.id == counselor_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="咨询师不存在")
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


# ── 排班查询 ──


@router.get("/counselors/{counselor_id}/schedule", response_model=ScheduleListResponse)
async def get_counselor_schedule(
    counselor_id: str,
    date_from: str = Query(..., description="YYYY-MM-DD"),
    date_to: str | None = None,
    db: AsyncSession = Depends(get_session),
    _user_id: str = Depends(_require_user),
):
    """查看咨询师可预约时段。"""
    d_from = date.fromisoformat(date_from)
    d_to = date.fromisoformat(date_to) if date_to else d_from

    stmt = (
        select(CounselorSchedule)
        .where(
            CounselorSchedule.counselor_id == counselor_id,
            CounselorSchedule.schedule_date >= d_from,
            CounselorSchedule.schedule_date <= d_to,
            CounselorSchedule.is_available.is_(True),
        )
        .order_by(CounselorSchedule.schedule_date, CounselorSchedule.start_time)
    )

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


# ── 预约 ──


@router.post("/appointments/create", response_model=AppointmentItem)
async def create_appointment(
    req: AppointmentCreateRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """创建预约。"""
    # 校验咨询师
    c_result = await db.execute(
        select(Counselor).where(Counselor.id == req.counselor_id, Counselor.status == "approved")
    )
    counselor = c_result.scalar_one_or_none()
    if not counselor:
        raise HTTPException(status_code=400, detail="咨询师不存在或未认证")

    # 校验预约配置
    settings_result = await db.execute(
        select(AppointmentSettings)
        .where(
            (AppointmentSettings.counselor_id == req.counselor_id)
            | (AppointmentSettings.counselor_id.is_(None))
        )
        .order_by(AppointmentSettings.counselor_id.desc().nullslast())
    )
    settings = settings_result.scalars().first()
    if settings and not settings.is_open:
        raise HTTPException(status_code=400, detail="预约已关闭")

    # 检查时段冲突
    appt_date = date.fromisoformat(req.appointment_date)
    appt_start = time.fromisoformat(req.start_time)
    conflict_stmt = select(Appointment).where(
        Appointment.counselor_id == req.counselor_id,
        Appointment.appointment_date == appt_date,
        Appointment.start_time == appt_start,
        Appointment.status.in_(["pending", "confirmed"]),
    )
    conflict = (await db.execute(conflict_stmt)).scalar_one_or_none()
    if conflict:
        raise HTTPException(status_code=400, detail="该时段已被预约")

    appointment = Appointment(
        counselor_id=req.counselor_id,
        user_id=user_id,
        schedule_id=req.schedule_id,
        appointment_date=appt_date,
        start_time=appt_start,
        end_time=time.fromisoformat(req.end_time),
        client_notes=req.client_notes,
    )
    db.add(appointment)
    await db.flush()
    await db.refresh(appointment)
    await db.commit()

    return AppointmentItem(
        id=appointment.id,
        counselor_id=appointment.counselor_id,
        counselor_name=counselor.real_name,
        user_id=appointment.user_id,
        appointment_date=appointment.appointment_date.isoformat(),
        start_time=appointment.start_time.strftime("%H:%M"),
        end_time=appointment.end_time.strftime("%H:%M"),
        status=appointment.status,
        cancel_reason=appointment.cancel_reason,
        client_notes=appointment.client_notes,
        created_at=appointment.created_at,
    )


@router.get("/appointments/list", response_model=AppointmentListResponse)
async def list_appointments(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """我的预约列表。"""
    stmt = select(Appointment).where(Appointment.user_id == user_id)
    if status:
        stmt = stmt.where(Appointment.status == status)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    appointments = result.scalars().all()

    items = []
    for a in appointments:
        c_result = await db.execute(select(Counselor).where(Counselor.id == a.counselor_id))
        c = c_result.scalar_one_or_none()
        items.append(
            AppointmentItem(
                id=a.id,
                counselor_id=a.counselor_id,
                counselor_name=c.real_name if c else None,
                user_id=a.user_id,
                appointment_date=a.appointment_date.isoformat(),
                start_time=a.start_time.strftime("%H:%M"),
                end_time=a.end_time.strftime("%H:%M"),
                status=a.status,
                cancel_reason=a.cancel_reason,
                client_notes=a.client_notes,
                created_at=a.created_at,
            )
        )
    return AppointmentListResponse(appointments=items, total=total)


@router.post("/appointments/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    req: AppointmentCancelRequest | None = None,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """取消预约。"""
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id, Appointment.user_id == user_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    if appointment.status not in ("pending", "confirmed"):
        raise HTTPException(status_code=400, detail="当前状态不可取消")

    appointment.status = "cancelled"
    appointment.cancel_reason = req.cancel_reason if req else None
    await db.commit()
    return {"success": True, "appointment_id": appointment.id, "status": "cancelled"}


# ── 订单 ──


@router.post("/orders/create", response_model=OrderItem)
async def create_order(
    req: OrderCreateRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """创建咨询订单。"""
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == req.appointment_id, Appointment.user_id == user_id
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")

    order = ConsultationOrder(
        appointment_id=req.appointment_id,
        counselor_id=appointment.counselor_id,
        user_id=user_id,
        order_type=req.order_type,
        package_name=req.package_name,
        amount=req.amount,
    )
    db.add(order)
    await db.flush()
    await db.refresh(order)
    await db.commit()

    return OrderItem(
        id=order.id,
        appointment_id=order.appointment_id,
        counselor_id=order.counselor_id,
        user_id=order.user_id,
        order_type=order.order_type,
        package_name=order.package_name,
        amount=order.amount,
        paid_amount=order.paid_amount,
        status=order.status,
        created_at=order.created_at,
    )


@router.get("/orders/list", response_model=OrderListResponse)
async def list_orders(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """我的订单列表。"""
    stmt = select(ConsultationOrder).where(ConsultationOrder.user_id == user_id)
    if status:
        stmt = stmt.where(ConsultationOrder.status == status)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(ConsultationOrder.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    orders = result.scalars().all()

    items = []
    for o in orders:
        c_result = await db.execute(select(Counselor).where(Counselor.id == o.counselor_id))
        c = c_result.scalar_one_or_none()
        items.append(
            OrderItem(
                id=o.id,
                appointment_id=o.appointment_id,
                counselor_id=o.counselor_id,
                counselor_name=c.real_name if c else None,
                user_id=o.user_id,
                order_type=o.order_type,
                package_name=o.package_name,
                amount=o.amount,
                paid_amount=o.paid_amount,
                status=o.status,
                created_at=o.created_at,
                paid_at=o.paid_at,
            )
        )
    return OrderListResponse(orders=items, total=total)


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: str,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """订单详情。"""
    result = await db.execute(
        select(ConsultationOrder).where(
            ConsultationOrder.id == order_id, ConsultationOrder.user_id == user_id
        )
    )
    o = result.scalar_one_or_none()
    if not o:
        raise HTTPException(status_code=404, detail="订单不存在")

    c_result = await db.execute(select(Counselor).where(Counselor.id == o.counselor_id))
    c = c_result.scalar_one_or_none()
    return OrderDetailResponse(
        id=o.id,
        appointment_id=o.appointment_id,
        counselor_id=o.counselor_id,
        counselor_name=c.real_name if c else None,
        user_id=o.user_id,
        order_type=o.order_type,
        package_name=o.package_name,
        amount=o.amount,
        paid_amount=o.paid_amount,
        status=o.status,
        wx_transaction_id=o.wx_transaction_id,
        created_at=o.created_at,
        paid_at=o.paid_at,
        refunded_at=o.refunded_at,
    )


# ── 支付 ──


@router.post("/orders/pay", response_model=PayResponse)
async def pay_order(
    req: PayRequest,
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
):
    """发起微信支付。"""
    result = await db.execute(
        select(ConsultationOrder).where(
            ConsultationOrder.id == req.order_id,
            ConsultationOrder.user_id == user_id,
            ConsultationOrder.status == "unpaid",
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=400, detail="订单不存在或已支付")

    out_trade_no = f"hushai_{order.id}"
    amount_cents = int(order.amount * 100)

    try:
        if req.pay_method == "jsapi":
            # 获取用户 openid
            from hushai.meditation.db.models import User

            u_result = await db.execute(select(User).where(User.id == user_id))
            user = u_result.scalar_one_or_none()
            if not user or not user.wx_openid:
                raise HTTPException(status_code=400, detail="缺少微信 openid，无法使用 JSAPI 支付")
            pay_result = await wechat_pay.create_jsapi_order(
                out_trade_no=out_trade_no,
                description="心理咨询服务",
                total_amount=amount_cents,
                openid=user.wx_openid,
            )
            order.wx_prepay_id = pay_result.get("prepay_id")
            await db.commit()
            return PayResponse(
                order_id=order.id,
                prepay_id=pay_result.get("prepay_id"),
                status="pending",
            )
        else:
            pay_result = await wechat_pay.create_native_order(
                out_trade_no=out_trade_no,
                description="心理咨询服务",
                total_amount=amount_cents,
            )
            return PayResponse(
                order_id=order.id,
                code_url=pay_result.get("code_url"),
                status="pending",
            )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.post("/orders/pay/notify")
async def pay_notify(request: Request, db: AsyncSession = Depends(get_session)):
    """微信支付回调通知。"""
    body = await request.body()
    headers = dict(request.headers)
    verified = wechat_pay.verify_notify_signature(headers, body)
    if not verified:
        raise HTTPException(status_code=400, detail="签名验证失败")

    result_data = wechat_pay.parse_notify_result(verified)
    out_trade_no = result_data.get("out_trade_no", "")
    trade_state = result_data.get("trade_state", "")

    if out_trade_no.startswith("hushai_"):
        order_id = out_trade_no[7:]  # strip "hushai_"
        o_result = await db.execute(
            select(ConsultationOrder).where(ConsultationOrder.id == order_id)
        )
        order = o_result.scalar_one_or_none()
        if order and trade_state == "SUCCESS":
            order.status = "paid"
            order.paid_amount = order.amount
            order.paid_at = datetime.now(timezone.utc)
            order.wx_transaction_id = result_data.get("transaction_id")
            await db.commit()
            logger.info("订单 %s 支付成功", order_id)

    return {"code": "SUCCESS", "message": "成功"}


# ── 服务记录 ──


@router.get("/service-records/list", response_model=ServiceRecordListResponse)
async def list_service_records(
    user_id: str = Depends(_require_user),
    db: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """我的咨询记录。"""
    stmt = select(ServiceRecord).where(ServiceRecord.user_id == user_id)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(ServiceRecord.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    records = result.scalars().all()

    items = []
    for r in records:
        c_result = await db.execute(select(Counselor).where(Counselor.id == r.counselor_id))
        c = c_result.scalar_one_or_none()
        items.append(
            ServiceRecordItem(
                id=r.id,
                order_id=r.order_id,
                appointment_id=r.appointment_id,
                counselor_id=r.counselor_id,
                counselor_name=c.real_name if c else None,
                user_id=r.user_id,
                service_type=r.service_type,
                duration_minutes=r.duration_minutes,
                status=r.status,
                started_at=r.started_at,
                ended_at=r.ended_at,
                created_at=r.created_at,
            )
        )
    return ServiceRecordListResponse(records=items, total=total)
