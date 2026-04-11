"""理论体系知识库 — RAG 导入与检索。"""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from hushai.meditation.config import get_config
from hushai.meditation.db import vector
from hushai.meditation.db.models import KnowledgeChunk


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """解析简单 YAML frontmatter（`---` 包裹，键值对）。"""
    t = text.lstrip("\ufeff")
    if not t.startswith("---"):
        return {}, text
    lines = t.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            body = "\n".join(lines[i + 1 :])
            return meta, body
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
        i += 1
    return {}, text


def _first_markdown_heading_title(body: str) -> str | None:
    for line in body.split("\n"):
        s = line.strip()
        m = re.match(r"^#{1,6}\s+(.+)$", s)
        if m:
            return m.group(1).strip()
    return None


def markdown_to_plain_text(md: str) -> str:
    """将 Markdown 转为适合向量检索的纯文本（无额外依赖）。"""
    t = md
    # fenced code blocks：保留内部文本
    t = re.sub(r"```[\w]*\n([\s\S]*?)```", lambda m: "\n" + m.group(1).strip() + "\n", t)
    t = re.sub(r"```([^`]+)```", lambda m: m.group(1), t)
    # inline code
    t = re.sub(r"`([^`]+)`", r"\1", t)
    # images then links
    t = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    # headers
    t = re.sub(r"^#{1,6}\s+(.+)$", r"\1", t, flags=re.MULTILINE)
    # bold / italic (order matters)
    t = re.sub(r"\*\*\*([^*]+)\*\*\*", r"\1", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", t)
    t = re.sub(r"__([^_]+)__", r"\1", t)
    t = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", t)
    # hr
    t = re.sub(r"^[-*_]{3,}\s*$", "", t, flags=re.MULTILINE)
    # lists
    t = re.sub(r"^\s*[-*+]\s+", "• ", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*\d+\.\s+", "", t, flags=re.MULTILINE)
    # blockquote
    t = re.sub(r"^>\s?", "", t, flags=re.MULTILINE)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def prepare_import_content(
    raw: str,
    *,
    filename: str | None,
    is_markdown: bool,
) -> tuple[str, str | None, list[str]]:
    """
    返回 (入库与分块的纯文本, 标题, 额外标签)。
    Markdown 会转纯文本以便与 Chroma 嵌入一致；并自动附加标签 `markdown`。
    """
    if not is_markdown:
        return raw.strip(), None, []

    extra_tags: list[str] = ["markdown"]
    meta, body = _split_frontmatter(raw)
    title = meta.get("title")
    tags_raw = meta.get("tags")
    if tags_raw:
        extra_tags.extend(
            [x.strip() for x in re.split(r"[,，]", tags_raw) if x.strip()]
        )

    plain = markdown_to_plain_text(body)
    if not title:
        title = _first_markdown_heading_title(body)
    if not title and filename:
        base = filename.rsplit("/", 1)[-1]
        title = base.rsplit(".", 1)[0] if "." in base else base

    return plain, title, extra_tags


def _split_text_to_chunks(
    text: str,
    chunk_size: int = 800,
    overlap: int = 200,
) -> list[str]:
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        while len(para) > chunk_size:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.append(para[:chunk_size])
            para = para[chunk_size:]
        if not para:
            continue
        if len(current) + len(para) + 2 > chunk_size and current:
            chunks.append(current.strip())
            tail = current[-overlap:] if len(current) > overlap else current
            current = tail + "\n\n" + para
        else:
            current = current + "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks


async def import_text(
    session: AsyncSession,
    content: str,
    title: str | None = None,
    tags: list[str] | None = None,
    parent_id: str | None = None,
    source: str | None = None,
) -> list[KnowledgeChunk]:
    chunks_text = _split_text_to_chunks(content)
    db_chunks: list[KnowledgeChunk] = []
    vector_data: list[dict[str, Any]] = []
    for i, chunk_text in enumerate(chunks_text):
        chunk = KnowledgeChunk(
            title=title if i == 0 else None,
            content=chunk_text,
            tags=tags or [],
            parent_id=parent_id,
            source=source,
            chunk_index=i,
        )
        session.add(chunk)
        await session.flush()
        db_chunks.append(chunk)
        vector_data.append(
            {
                "id": chunk.id,
                "content": chunk_text,
                "title": title,
                "tags": tags or [],
                "source": source,
                "parent_id": parent_id,
            }
        )
    vector.add_knowledge_chunks(vector_data)
    return db_chunks


async def import_structured(
    session: AsyncSession,
    data: dict[str, Any],
    parent_id: str | None = None,
) -> list[KnowledgeChunk]:
    results: list[KnowledgeChunk] = []
    title = data.get("title", "")
    content = data.get("content", "")
    tags = data.get("tags", [])
    source = data.get("source")
    if content:
        chunks = await import_text(
            session,
            content,
            title=title,
            tags=tags,
            parent_id=parent_id,
            source=source,
        )
        parent_id_for_children = chunks[0].id if chunks else None
        results.extend(chunks)
    else:
        parent_id_for_children = parent_id
    for child in data.get("children", []):
        child_chunks = await import_structured(
            session,
            child,
            parent_id=parent_id_for_children,
        )
        results.extend(child_chunks)
    return results


async def search_knowledge_base(
    query: str,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    cfg = get_config()
    top_k = top_k or cfg.knowledge_top_k
    return vector.search_knowledge(query, top_k=top_k)


async def get_knowledge_context_for_prompt(query: str) -> str:
    results = await search_knowledge_base(query)
    if not results:
        return ""
    lines: list[str] = ["【相关理论参考】"]
    for r in results:
        source_info = f"（来源: {r.get('source', '未知')}）" if r.get("source") else ""
        lines.append(f"- {r['content'][:200]}{source_info}")
    return "\n".join(lines)
