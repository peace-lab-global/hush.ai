"""知识库管理 API 路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.knowledge import import_structured, import_text, search_knowledge_base
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ErrorResponse,
    KnowledgeImportRequest,
    KnowledgeItem,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


async def _require_admin(
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_session),
) -> str:
    token = extract_bearer_token(authorization)
    try:
        return await get_current_user_id(token, session)
    except RuntimeError as e:
        raise HTTPException(status_code=401, detail=str(e)) from None


@router.post(
    "/import",
    response_model=list[KnowledgeItem],
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge(
    req: KnowledgeImportRequest,
    session: AsyncSession = Depends(get_session),
    _admin: str = Depends(_require_admin),
) -> list[KnowledgeItem]:
    chunks = await import_text(
        session,
        content=req.content,
        title=req.title,
        tags=req.tags,
        parent_id=req.parent_id,
    )
    await session.commit()
    return [
        KnowledgeItem(
            id=c.id,
            title=c.title,
            content=c.content,
            tags=c.tags or [],
            parent_id=c.parent_id,
            created_at=c.created_at,
        )
        for c in chunks
    ]


@router.post(
    "/import-file",
    response_model=list[KnowledgeItem],
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge_file(
    file: UploadFile = File(...),
    tags: str = "",
    parent_id: str | None = None,
    session: AsyncSession = Depends(get_session),
    _admin: str = Depends(_require_admin),
) -> list[KnowledgeItem]:
    content = (await file.read()).decode("utf-8")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    chunks = await import_text(
        session,
        content=content,
        title=file.filename,
        tags=tag_list,
        parent_id=parent_id,
        source=file.filename,
    )
    await session.commit()
    return [
        KnowledgeItem(
            id=c.id,
            title=c.title,
            content=c.content,
            tags=c.tags or [],
            parent_id=c.parent_id,
            created_at=c.created_at,
        )
        for c in chunks
    ]


@router.post(
    "/import-structured",
    response_model=list[KnowledgeItem],
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge_structured(
    data: dict[str, Any],
    session: AsyncSession = Depends(get_session),
    _admin: str = Depends(_require_admin),
) -> list[KnowledgeItem]:
    chunks = await import_structured(session, data)
    await session.commit()
    return [
        KnowledgeItem(
            id=c.id,
            title=c.title,
            content=c.content,
            tags=c.tags or [],
            parent_id=c.parent_id,
            created_at=c.created_at,
        )
        for c in chunks
    ]


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    responses={401: {"model": ErrorResponse}},
)
async def search_knowledge(
    req: KnowledgeSearchRequest,
    _admin: str = Depends(_require_admin),
) -> KnowledgeSearchResponse:
    results = await search_knowledge_base(req.query, top_k=req.top_k)
    return KnowledgeSearchResponse(
        results=[
            KnowledgeSearchResult(
                id=r["id"],
                title=r.get("title"),
                content=r["content"],
                score=r["score"],
                tags=r.get("tags", []),
            )
            for r in results
        ]
    )
