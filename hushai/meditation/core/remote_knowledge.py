"""远程知识源 — 支持从 Coze、IMA 或任意 URL 抓取 MD 文档并入库。"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from hushai.meditation.config import get_config
from hushai.meditation.core.knowledge import (
    import_text,
    prepare_import_content,
)

logger = logging.getLogger(__name__)

FETCH_TIMEOUT = 30.0
MAX_CONCURRENT_FETCHES = 5


@dataclass
class RemoteDocument:
    """远程文档元数据。"""

    url: str
    title: str = ""
    tags: list[str] = field(default_factory=list)
    source: str = ""


class RemoteSourceAdapter(Protocol):
    """远程源适配器协议。"""

    async def list_documents(self, config: dict[str, str]) -> list[RemoteDocument]: ...

    def source_label(self) -> str: ...


# ── URL 源 ──────────────────────────────────────────────


class URLSourceAdapter:
    """通用 URL 源：从 HTTP(S) 直接拉取 Markdown/文本文件。"""

    def source_label(self) -> str:
        return "url"

    async def list_documents(self, config: dict[str, str]) -> list[RemoteDocument]:
        urls_s = config.get("urls", "")
        if not urls_s.strip():
            return []
        docs: list[RemoteDocument] = []
        for line in urls_s.strip().split("\n"):
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            docs.append(RemoteDocument(url=url, source="url"))
        return docs


# ── Coze 源 ─────────────────────────────────────────────


class CozeSourceAdapter:
    """Coze 知识库源：通过 Coze API 拉取文档列表和内容。

    Coze API 参考:
      - 文档列表: GET /v1/knowledge/document/list?dataset_id=xxx
      - 文档内容: GET /v1/knowledge/document/{document_id}
      - Token 通过 Personal Access Token 传入

    配置字段:
      - api_base: Coze API 地址 (默认 https://api.coze.cn)
      - api_token: Coze Personal Access Token
      - dataset_id: 知识库 ID
    """

    def source_label(self) -> str:
        return "coze"

    async def list_documents(self, config: dict[str, str]) -> list[RemoteDocument]:
        api_base = config.get("api_base", "https://api.coze.cn").rstrip("/")
        api_token = config.get("api_token", "")
        dataset_id = config.get("dataset_id", "")

        if not api_token or not dataset_id:
            logger.warning("Coze 源缺少 api_token 或 dataset_id，跳过")
            return []

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        docs: list[RemoteDocument] = []
        page_num = 1
        page_size = 50

        async with httpx.AsyncClient(timeout=FETCH_TIMEOUT) as client:
            while True:
                try:
                    resp = await client.get(
                        f"{api_base}/v1/knowledge/document/list",
                        headers=headers,
                        params={
                            "dataset_id": dataset_id,
                            "page_num": page_num,
                            "page_size": page_size,
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    logger.error("Coze 文档列表拉取失败: %s", e)
                    break

                if data.get("code") != 0:
                    logger.error("Coze API 返回错误: %s", data.get("msg", "未知错误"))
                    break

                doc_list = data.get("data", {}).get("document_list", [])
                for d in doc_list:
                    doc_id = d.get("document_id", "")
                    title = d.get("name", "") or d.get("title", "")
                    doc_url = f"{api_base}/v1/knowledge/document/{doc_id}"
                    docs.append(
                        RemoteDocument(
                            url=doc_url,
                            title=title,
                            tags=["coze"],
                            source="coze",
                        )
                    )

                total = data.get("data", {}).get("total", 0)
                if page_num * page_size >= total:
                    break
                page_num += 1

        return docs


# ── IMA 源 ──────────────────────────────────────────────

# IMA (腾讯智能助手) 目前主要通过客户端使用，开放 API 有限。
# 此处提供 URL 适配模式：用户在 IMA 中将文档导出/分享链接，通过 URL 抓取。


class IMASourceAdapter:
    """IMA 知识源适配器：通过分享链接或导出 URL 拉取文档。

    配置字段:
      - urls: 文档 URL 列表（每行一个）
      - cookie: IMA 登录态 Cookie（如需鉴权）
    """

    def source_label(self) -> str:
        return "ima"

    async def list_documents(self, config: dict[str, str]) -> list[RemoteDocument]:
        urls_s = config.get("urls", "")
        if not urls_s.strip():
            return []
        docs: list[RemoteDocument] = []
        for line in urls_s.strip().split("\n"):
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            docs.append(RemoteDocument(url=url, tags=["ima"], source="ima"))
        return docs


# ── 抓取引擎 ────────────────────────────────────────────


_ADAPTERS: dict[str, RemoteSourceAdapter] = {
    "url": URLSourceAdapter(),
    "coze": CozeSourceAdapter(),
    "ima": IMASourceAdapter(),
}


def _resolve_filename_from_url(url: str) -> str:
    """从 URL 路径提取文件名。"""
    try:
        path = url.split("?")[0].split("#")[0]
        name = path.rsplit("/", 1)[-1]
        if name:
            return name
    except Exception:
        pass
    return "remote_doc.md"


async def _fetch_single(
    client: httpx.AsyncClient,
    doc: RemoteDocument,
    extra_headers: dict[str, str] | None = None,
) -> tuple[str, str, list[str], str] | None:
    """抓取单个文档，返回 (内容, 标题, 标签, 源名) 或 None。"""
    headers: dict[str, str] = {
        "User-Agent": "hush.ai/1.0 (+https://github.com/peace-lab-global/hush.ai)",
    }
    if extra_headers:
        headers.update(extra_headers)

    try:
        resp = await client.get(doc.url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
        content = resp.text
    except Exception as e:
        logger.warning("抓取失败 %s: %s", doc.url, e)
        return None

    if not content.strip():
        return None

    fn = _resolve_filename_from_url(doc.url)
    is_md = fn.lower().endswith((".md", ".markdown")) or "markdown" in str(
        resp.headers.get("content-type", "")
    ).lower()
    return content, doc.title or fn, doc.tags, doc.source


async def fetch_and_import_urls(
    urls: list[str],
    tags: list[str] | None = None,
    session=None,  # AsyncSession
) -> dict[str, Any]:
    """从 URL 列表抓取 MD 文档并直接导入知识库。

    Args:
        urls: 文档 URL 列表
        tags: 额外标签
        session: 数据库会话（如果提供则直接导入）

    Returns:
        {"imported": int, "results": [...], "errors": [...]}
    """
    if not session:
        return {"imported": 0, "results": [], "errors": ["缺少数据库会话"]}

    docs = [RemoteDocument(url=u, tags=tags or [], source="url") for u in urls if u.strip()]
    return await _import_documents(docs, {}, session)


async def fetch_from_remote_source(
    source_type: str,
    config: dict[str, str],
    session=None,
) -> dict[str, Any]:
    """从指定远程源类型拉取文档列表并导入。

    Args:
        source_type: 源类型 (url/coze/ima)
        config: 源配置 (api_key, urls 等)
        session: 数据库会话

    Returns:
        {"imported": int, "results": [...], "errors": [...]}
    """
    if not session:
        return {"imported": 0, "results": [], "errors": ["缺少数据库会话"]}

    adapter = _ADAPTERS.get(source_type)
    if not adapter:
        return {"imported": 0, "results": [], "errors": [f"不支持的源类型: {source_type}"]}

    try:
        docs = await adapter.list_documents(config)
    except Exception as e:
        logger.error("列出文档失败 (%s): %s", source_type, e)
        return {"imported": 0, "results": [], "errors": [f"列出文档失败: {e}"]}

    if not docs:
        return {"imported": 0, "results": [], "errors": ["未找到可导入文档"]}

    extra_headers: dict[str, str] = {}
    if source_type == "coze":
        api_token = config.get("api_token", "")
        if api_token:
            extra_headers["Authorization"] = f"Bearer {api_token}"
    elif source_type == "ima":
        cookie = config.get("cookie", "")
        if cookie:
            extra_headers["Cookie"] = cookie

    return await _import_documents(docs, extra_headers, session)


async def _import_documents(
    docs: list[RemoteDocument],
    extra_headers: dict[str, str],
    session,
) -> dict[str, Any]:
    """内部：抓取并导入文档列表。"""
    from hushai.meditation.core.knowledge import import_text, prepare_import_content

    results: list[dict[str, Any]] = []
    errors: list[str] = []

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

    async def _fetch_one(doc: RemoteDocument) -> None:
        async with semaphore:
            async with httpx.AsyncClient(timeout=FETCH_TIMEOUT) as client:
                fetched = await _fetch_single(client, doc, extra_headers)
        if fetched is None:
            errors.append(f"{doc.url}: 抓取失败")
            return
        content, title, fetch_tags, source = fetched
        fn = _resolve_filename_from_url(doc.url)
        is_md = fn.lower().endswith((".md", ".markdown"))
        try:
            plain, derived_title, extra_tags = prepare_import_content(
                content, filename=fn, is_markdown=is_md
            )
        except Exception as e:
            errors.append(f"{doc.url}: 解析失败 - {e}")
            return
        if not plain.strip():
            errors.append(f"{doc.url}: 解析后内容为空")
            return

        final_title = title or derived_title or fn
        final_tags = list(dict.fromkeys([*fetch_tags, *extra_tags]))

        try:
            chunks = await import_text(
                session,
                content=plain,
                title=final_title,
                tags=final_tags,
                source=source or doc.url,
            )
            results.append(
                {
                    "url": doc.url,
                    "title": final_title,
                    "chunks": len(chunks),
                    "source": source,
                }
            )
            logger.info("导入成功: %s (%d chunks)", doc.url, len(chunks))
        except Exception as e:
            errors.append(f"{doc.url}: 入库失败 - {e}")

    tasks = [_fetch_one(d) for d in docs]
    await asyncio.gather(*tasks)

    try:
        await session.commit()
    except Exception as e:
        logger.error("提交失败: %s", e)
        await session.rollback()

    return {"imported": len(results), "results": results, "errors": errors}


async def sync_all_remote_sources(session=None) -> dict[str, Any]:
    """同步所有已配置的远程知识源。

    从 MeditationConfig.remote_knowledge_sources 读取配置，
    逐一拉取并导入。
    """
    if not session:
        return {"synced": 0, "sources": [], "errors": ["缺少数据库会话"]}

    cfg = get_config()
    sources = cfg.remote_knowledge_sources
    if not sources:
        return {"synced": 0, "sources": [], "errors": ["未配置远程知识源"]}

    all_results: list[dict[str, Any]] = []
    total_imported = 0

    for source_name, source_config in sources.items():
        source_type = source_config.get("type", "url")
        logger.info("同步远程源: %s (type=%s)", source_name, source_type)
        result = await fetch_from_remote_source(source_type, source_config, session)
        result["source_name"] = source_name
        all_results.append(result)
        total_imported += result.get("imported", 0)

    return {"synced": total_imported, "sources": all_results, "errors": []}
