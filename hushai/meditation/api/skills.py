"""技能列表与批量导入（导入需管理员或用户 JWT）。"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import verify_admin_token
from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.db.models import Skill
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ErrorResponse,
    SkillImportedRow,
    SkillImportRequest,
    SkillImportResult,
    SkillListResponse,
    SkillPublicItem,
)

router = APIRouter(prefix="/api/skills", tags=["skills"])


async def _require_skills_operator(
    authorization: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    """允许管理员 JWT（后台导入）或普通用户 JWT。"""
    if not authorization:
        raise HTTPException(status_code=401, detail="缺少 Authorization")
    token = extract_bearer_token(authorization)
    try:
        verify_admin_token(token)
        return "__admin__"
    except RuntimeError:
        pass
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.get("/", response_model=SkillListResponse)
async def list_active_skills(session: AsyncSession = Depends(get_session)) -> SkillListResponse:
    stmt = (
        select(Skill)
        .where(Skill.is_active.is_(True))
        .order_by(Skill.sort_order.asc(), Skill.name.asc())
    )
    result = await session.execute(stmt)
    rows = list(result.scalars().all())
    return SkillListResponse(
        skills=[SkillPublicItem(id=s.id, name=s.name, description=s.description) for s in rows]
    )


@router.post(
    "/import",
    response_model=SkillImportResult,
    responses={401: {"model": ErrorResponse}},
)
async def import_skills(
    req: SkillImportRequest,
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_skills_operator),
) -> SkillImportResult:
    created: list[Skill] = []
    for item in req.skills:
        desc = item.description
        if desc is not None and len(desc) > 512:
            desc = desc[:512]
        s = Skill(
            name=item.name[:128],
            description=desc,
            content=item.content,
            sort_order=item.sort_order,
            is_active=item.is_active,
        )
        session.add(s)
        created.append(s)
    await session.flush()
    await session.commit()
    return SkillImportResult(
        imported=len(created),
        items=[SkillImportedRow(id=s.id, name=s.name) for s in created],
    )


@router.post(
    "/import-file",
    response_model=SkillImportResult,
    responses={401: {"model": ErrorResponse}},
)
async def import_skills_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_skills_operator),
) -> SkillImportResult:
    raw = (await file.read()).decode("utf-8")
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON 解析失败: {e}") from None
    try:
        req = SkillImportRequest.model_validate(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"数据格式无效: {e}") from None
    return await import_skills(req, session, _operator)
