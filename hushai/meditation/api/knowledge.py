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
from hushai.meditation.core.remote_knowledge import (
    fetch_and_import_urls,
    fetch_from_remote_source,
    sync_all_remote_sources,
)
from hushai.meditation.db.session import get_session
from hushai.meditation.schemas import (
    ErrorResponse,
    KnowledgeImportRequest,
    KnowledgeItem,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    RemoteImportRequest,
    RemoteImportResult,
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
    plain, derived_title, extra_tags = prepare_import_content(raw, filename=fn, is_markdown=is_md)
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
    "/import-batch",
    response_model=dict,
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge_batch(
    files: list[UploadFile] = File(...),
    tags: str = "",
    as_markdown: bool = Form(False),
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> dict:
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for f in files:
        try:
            raw_bytes = await f.read()
            try:
                raw = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw = raw_bytes.decode("gbk", errors="replace")
            fn = f.filename or "upload.txt"
            is_md = bool(as_markdown) or fn.lower().endswith((".md", ".markdown"))
            plain, derived_title, extra_tags = prepare_import_content(
                raw,
                filename=fn,
                is_markdown=is_md,
            )
            if not plain.strip():
                errors.append(f"{fn}: 解析后内容为空")
                continue
            tags_merged = list(dict.fromkeys([*tag_list, *extra_tags]))
            title = derived_title or fn
            chunks = await import_text(
                session,
                content=plain,
                title=title,
                tags=tags_merged,
                source=fn,
            )
            results.append({"filename": fn, "chunks": len(chunks), "title": title})
        except Exception as e:
            errors.append(f"{f.filename}: {e}")
    await session.commit()
    return {"imported": len(results), "results": results, "errors": errors}


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


@router.post(
    "/import-url",
    response_model=RemoteImportResult,
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge_from_urls(
    req: RemoteImportRequest,
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> RemoteImportResult:
    """从 URL 列表抓取 Markdown 文档并入库。

    支持 GitHub raw、Coze 分享链接、IMA 导出链接等任意 HTTP(S) 地址。
    当 source_type="url" 或 "ima" 时，直接使用 urls 字段的列表抓取。
    """
    if req.source_type in ("url", "ima"):
        if not req.urls:
            raise HTTPException(status_code=400, detail="URL 列表不能为空")
        result = await fetch_and_import_urls(req.urls, tags=req.tags, session=session)
    elif req.source_type == "coze":
        result = await fetch_from_remote_source("coze", req.config, session=session)
    else:
        raise HTTPException(status_code=400, detail=f"不支持的源类型: {req.source_type}")

    await session.commit()
    return RemoteImportResult(
        imported=result.get("imported", 0),
        results=result.get("results", []),
        errors=result.get("errors", []),
    )


@router.post(
    "/import-remote",
    response_model=RemoteImportResult,
    responses={401: {"model": ErrorResponse}},
)
async def import_knowledge_from_remote_source(
    req: RemoteImportRequest,
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> RemoteImportResult:
    """从指定远程知识源（Coze/IMA/URL）拉取文档并入库。

    - source_type="coze": 需在 config 中提供 api_token、dataset_id
    - source_type="ima": 需在 config 中提供 urls 列表，可选 cookie
    - source_type="url": 使用 urls 字段的列表直接抓取
    """
    result = await fetch_from_remote_source(req.source_type, req.config, session=session)
    await session.commit()
    return RemoteImportResult(
        imported=result.get("imported", 0),
        results=result.get("results", []),
        errors=result.get("errors", []),
    )


@router.post(
    "/sync-remote",
    response_model=dict,
    responses={401: {"model": ErrorResponse}},
)
async def sync_remote_knowledge_sources(
    session: AsyncSession = Depends(get_session),
    _operator: str = Depends(_require_knowledge_operator),
) -> dict:
    """一键同步所有已配置的远程知识源。

    从系统配置中的 remote_knowledge_sources 读取所有源配置并逐一拉取导入。
    """
    result = await sync_all_remote_sources(session=session)
    await session.commit()
    return result
