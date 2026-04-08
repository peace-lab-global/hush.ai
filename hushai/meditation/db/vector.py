"""ChromaDB 向量数据库接口。"""

from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from hushai.meditation.config import get_config

_client: chromadb.ClientAPI | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        cfg = get_config()
        if cfg.chroma_persist_dir:
            _client = chromadb.PersistentClient(
                path=cfg.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        else:
            _client = chromadb.Client(
                settings=ChromaSettings(anonymized_telemetry=False),
            )
    return _client


def reset_vector_for_tests() -> None:
    global _client
    _client = None


def _build_collection_kwargs() -> dict[str, Any]:
    ef = _make_embedding_function()
    if ef is not None:
        return {"embedding_function": ef}
    return {}


def _make_embedding_function() -> Any:
    cfg = get_config()
    provider = cfg.embedding_provider
    if provider == "openai":
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

        api_key = cfg.embedding_api_key or cfg.openai_api_key
        base_url = cfg.embedding_base_url or cfg.openai_base_url or None
        return OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=cfg.embedding_model,
            api_base=base_url,
        )
    return None


def knowledge_collection() -> chromadb.Collection:
    kwargs = _build_collection_kwargs()
    client = _get_client()
    return client.get_or_create_collection(
        name="knowledge",
        metadata={"hnsw:space": "cosine"},
        **kwargs,
    )


def memory_collection() -> chromadb.Collection:
    kwargs = _build_collection_kwargs()
    client = _get_client()
    return client.get_or_create_collection(
        name="memories",
        metadata={"hnsw:space": "cosine"},
        **kwargs,
    )


def add_knowledge_chunks(
    chunks: list[dict[str, Any]],
) -> None:
    if not chunks:
        return
    col = knowledge_collection()
    ids = [c["id"] for c in chunks]
    documents = [c["content"] for c in chunks]
    metadatas = []
    for c in chunks:
        meta: dict[str, Any] = {}
        if c.get("title"):
            meta["title"] = c["title"]
        if c.get("tags"):
            meta["tags"] = ",".join(c["tags"])
        if c.get("source"):
            meta["source"] = c["source"]
        if c.get("parent_id"):
            meta["parent_id"] = c["parent_id"]
        metadatas.append(meta)
    col.upsert(ids=ids, documents=documents, metadatas=metadatas)


def search_knowledge(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    col = knowledge_collection()
    count = col.count()
    if count == 0:
        return []
    results = col.query(query_texts=[query], n_results=min(top_k, count))
    items: list[dict[str, Any]] = []
    if not results["ids"] or not results["ids"][0]:
        return items
    for i, doc_id in enumerate(results["ids"][0]):
        doc = results["documents"][0][i] if results["documents"] else ""
        dist = results["distances"][0][i] if results["distances"] else 0.0
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append(
            {
                "id": doc_id,
                "content": doc,
                "score": 1.0 - dist,
                "title": meta.get("title"),
                "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
                "source": meta.get("source"),
            }
        )
    return items


def add_memory_embedding(
    memory_id: str,
    content: str,
    user_id: str,
    category: str,
) -> None:
    col = memory_collection()
    col.upsert(
        ids=[memory_id],
        documents=[content],
        metadatas=[{"user_id": user_id, "category": category}],
    )


def search_memories(
    query: str,
    user_id: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    col = memory_collection()
    count = col.count()
    if count == 0:
        return []
    results = col.query(
        query_texts=[query],
        n_results=min(top_k, count),
        where={"user_id": user_id},
    )
    items: list[dict[str, Any]] = []
    if not results["ids"] or not results["ids"][0]:
        return items
    for i, doc_id in enumerate(results["ids"][0]):
        doc = results["documents"][0][i] if results["documents"] else ""
        dist = results["distances"][0][i] if results["distances"] else 0.0
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append(
            {
                "id": doc_id,
                "content": doc,
                "score": 1.0 - dist,
                "category": meta.get("category", ""),
            }
        )
    return items


def delete_memory_embedding(memory_id: str) -> None:
    col = memory_collection()
    col.delete(ids=[memory_id])
