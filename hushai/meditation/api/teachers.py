"""冥想导师角色 API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import get_current_user_id
from hushai.meditation.db.models import Teacher, User
from hushai.meditation.db.session import get_session

router = APIRouter(prefix="/api/teachers", tags=["teachers"])


class TeacherItem(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    avatar: str | None
    voice_gender: str | None
    style_tags: str | None


class TeacherListResponse(BaseModel):
    teachers: list[TeacherItem]
    selected_id: str | None


class TeacherDetailResponse(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    avatar: str | None
    default_voice: str | None
    voice_gender: str | None
    style_tags: str | None


@router.get("/list", response_model=TeacherListResponse)
async def list_teachers(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Teacher).where(Teacher.is_active == True).order_by(Teacher.sort_order.asc())
    )
    teachers = result.scalars().all()

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    selected_id = user.selected_teacher_id if user else None

    return TeacherListResponse(
        teachers=[
            TeacherItem(
                id=t.id,
                name=t.name,
                slug=t.slug,
                description=t.description,
                avatar=t.avatar,
                voice_gender=t.voice_gender,
                style_tags=t.style_tags,
            )
            for t in teachers
        ],
        selected_id=selected_id,
    )


@router.get("/{teacher_id}", response_model=TeacherDetailResponse)
async def get_teacher(
    teacher_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="导师不存在")

    return TeacherDetailResponse(
        id=teacher.id,
        name=teacher.name,
        slug=teacher.slug,
        description=teacher.description,
        avatar=teacher.avatar,
        default_voice=teacher.default_voice,
        voice_gender=teacher.voice_gender,
        style_tags=teacher.style_tags,
    )


class SelectTeacherRequest(BaseModel):
    teacher_id: str


class SelectTeacherResponse(BaseModel):
    success: bool
    teacher_id: str


@router.post("/select", response_model=SelectTeacherResponse)
async def select_teacher(
    req: SelectTeacherRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Teacher).where(Teacher.id == req.teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="导师不存在")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.selected_teacher_id = req.teacher_id
        await db.commit()

    return SelectTeacherResponse(success=True, teacher_id=req.teacher_id)
