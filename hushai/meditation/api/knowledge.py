"""知识库管理 API 路由。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.admin.auth import verify_admin_token
from hushai.meditation.api.auth import extract_bearer_token, get_current_user_id
from hushai.meditation.core.knowledge import (
    import_structured,
    import_text,
    prepare_import_content,
    search_knowledge_base,
)
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


async def _require_knowledge_operator(
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


@router.post(
    "/import",
    response_model=list[KnowledgeItem],
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge(
    req: KnowledgeImportRequest,
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> list[KnowledgeItem]:
    is_md = req.content_format == "markdown"
    plain, derived_title, extra_tags = prepare_import_content(
        req.content, filename=None, is_markdown=is_md
    )
    if not plain.strip():
        raise HTTPException(status_code=400, detail="导入内容解析后为空")
    title = req.title or derived_title
    tags = list(dict.fromkeys([*req.tags, *extra_tags]))
    chunks = await import_text(
        session,
        content=plain,
        title=title,
        tags=tags,
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
    as_markdown: bool = Form(False),
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> list[KnowledgeItem]:
    raw = (await file.read()).decode("utf-8")
    fn = file.filename or "upload.txt"
    is_md = bool(as_markdown) or fn.lower().endswith((".md", ".markdown"))
    plain, derived_title, extra_tags = prepare_import_content(
        raw, filename=fn, is_markdown=is_md
    )
    if not plain.strip():
        raise HTTPException(status_code=400, detail="文件解析后内容为空")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    tags_merged = list(dict.fromkeys([*tag_list, *extra_tags]))
    title = derived_title or fn
    chunks = await import_text(
        session,
        content=plain,
        title=title,
        tags=tags_merged,
        parent_id=parent_id,
        source=fn,
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
    _operator: str = Depends(_require_knowledge_operator),
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
    _operator: str = Depends(_require_knowledge_operator),
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
