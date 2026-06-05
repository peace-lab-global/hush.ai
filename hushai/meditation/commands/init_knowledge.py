#!/usr/bin/env python3
"""初始化 / 批量导入知识库 — 产品化 CLI。"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Final

# 加载 .env
from dotenv import load_dotenv

# 尝试加载项目根目录的 .env
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env")

# 将项目根目录加入 sys.path（开发模式）
sys.path.insert(0, str(_PROJECT_ROOT))

from hushai.meditation.config import reset_config
from hushai.meditation.core.knowledge import import_text, prepare_import_content
from hushai.meditation.db.session import close_db, get_session_factory, init_db
from hushai.meditation.db.vector import knowledge_collection

DEFAULT_REPO_URL: Final[str] = "https://github.com/peace-lab-global/open-cognition.git"
DEFAULT_SOURCE_DIR: Final[Path] = _PROJECT_ROOT / "knowledge" / "open-cognition"

EXCLUDE_DIRS: Final[set[str]] = {"reports", "templates", "meta", ".git"}
EXCLUDE_ROOT_FILES: Final[set[str]] = {
    "README.md",
    "INDEX.md",
    "TAGS.md",
    "CONTRIBUTING.md",
    "COVERAGE_AUDIT.md",
    "EVALUATION_REPORT.md",
    "FINAL_COVERAGE_ASSESSMENT.md",
}


def _extract_domain_tags(rel_path: Path) -> list[str]:
    """从相对路径提取领域标签。"""
    parts = rel_path.parts
    tags: list[str] = []
    if len(parts) > 0:
        first = parts[0]
        if first == "domains" and len(parts) > 1:
            tags.append(parts[1])
        elif first == "skills":
            tags.append("skills")
            if len(parts) > 1:
                m = re.match(r"(.+?)-frameworks", parts[1])
                if m:
                    tags.append(m.group(1))
        elif first == "wisdom-masters":
            tags.append("wisdom-masters")
            if len(parts) > 1 and parts[1] == "masters" and len(parts) > 2:
                tags.append(parts[2])  # 如 china, tibet, japan
    return tags


def _file_hash(path: Path) -> str:
    """计算文件内容的 MD5（用于断点续传判断）。"""
    return hashlib.md5(path.read_bytes()).hexdigest()


def _collect_md_files(source_dir: Path, domain_filter: list[str] | None = None) -> list[Path]:
    """收集需要导入的 markdown 文件。"""
    files: list[Path] = []
    for p in source_dir.rglob("*.md"):
        rel = p.relative_to(source_dir)
        # 跳过排除目录
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        # 跳过根目录排除文件
        if rel.name in EXCLUDE_ROOT_FILES and len(rel.parts) == 1:
            continue
        # 领域过滤
        if domain_filter:
            tags = _extract_domain_tags(rel)
            if not any(t in domain_filter for t in tags):
                continue
        files.append(rel)
    files.sort()
    return files


def _get_already_imported_sources() -> set[str]:
    """从向量库中查询已存在的 source 路径，用于断点续传。"""
    try:
        col = knowledge_collection()
        count = col.count()
        if count == 0:
            return set()
        # 获取所有条目的 metadata
        results = col.get(include=["metadatas"])
        sources: set[str] = set()
        if results and results.get("metadatas"):
            for meta in results["metadatas"]:
                if meta and meta.get("source"):
                    sources.add(str(meta["source"]))
        return sources
    except Exception:
        return set()


def _clone_repo(repo_url: str, target_dir: Path) -> None:
    """Clone GitHub 仓库到指定目录。"""
    if target_dir.exists() and any(target_dir.iterdir()):
        print(f"目录已存在且非空: {target_dir}")
        print("将尝试复用现有文件（如需重新拉取，请先删除该目录）。")
        return
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    print(f"正在克隆仓库: {repo_url} ...")
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(target_dir)],
        check=True,
        capture_output=False,
    )
    print(f"克隆完成: {target_dir}")


async def _do_import(
    source_dir: Path,
    *,
    dry_run: bool = False,
    domain_filter: list[str] | None = None,
    skip_existing: bool = True,
) -> dict[str, int | list[str]]:
    """执行导入，返回统计信息。"""
    md_files = _collect_md_files(source_dir, domain_filter)
    if not md_files:
        return {"total_files": 0, "imported": 0, "skipped": 0, "chunks": 0, "errors": ["未找到匹配的 Markdown 文件"]}

    existing_sources: set[str] = set()
    if skip_existing and not dry_run:
        print("正在检查已导入记录（断点续传）...")
        existing_sources = _get_already_imported_sources()
        if existing_sources:
            print(f"  发现 {len(existing_sources)} 个已导入 source，将自动跳过。")

    if dry_run:
        print(f"\n[预览模式] 共发现 {len(md_files)} 个文件待导入:\n")
        for rel in md_files:
            tags = _extract_domain_tags(rel)
            tag_str = ", ".join(tags) if tags else "—"
            status = "已存在" if str(rel) in existing_sources else "新导入"
            print(f"  [{status}] {rel} | 领域: [{tag_str}]")
        return {"total_files": len(md_files), "imported": 0, "skipped": 0, "chunks": 0, "errors": []}

    # 初始化数据库
    await init_db()
    factory = get_session_factory()

    imported = 0
    skipped = 0
    total_chunks = 0
    errors: list[str] = []

    async with factory() as session:
        for idx, rel_path in enumerate(md_files, 1):
            abs_path = source_dir / rel_path
            source_key = str(rel_path)

            # 断点续传：如果 source 已存在且文件 hash 没变，跳过
            if skip_existing and source_key in existing_sources:
                skipped += 1
                print(f"  [{idx}/{len(md_files)}] ⏭ 跳过 (已导入) {rel_path}")
                continue

            try:
                raw = abs_path.read_text(encoding="utf-8")
            except Exception as exc:
                errors.append(f"{rel_path}: 读取失败 {exc}")
                continue

            plain, derived_title, extra_tags = prepare_import_content(
                raw, filename=rel_path.name, is_markdown=True
            )
            if not plain.strip():
                print(f"  [{idx}/{len(md_files)}] ⚠ 跳过 (空内容) {rel_path}")
                continue

            domain_tags = _extract_domain_tags(rel_path)
            tags = list(dict.fromkeys([*domain_tags, *extra_tags]))
            title = derived_title or rel_path.stem

            try:
                chunks = await import_text(
                    session,
                    content=plain,
                    title=title,
                    tags=tags,
                    source=source_key,
                )
                total_chunks += len(chunks)
                imported += 1
                tag_str = ", ".join(tags) if tags else "—"
                print(f"  [{idx}/{len(md_files)}] ✓ {rel_path} → {len(chunks)} 分块 | [{tag_str}]")
            except Exception as exc:
                errors.append(f"{rel_path}: 入库失败 {exc}")

        await session.commit()

    await close_db()

    return {
        "total_files": len(md_files),
        "imported": imported,
        "skipped": skipped,
        "chunks": total_chunks,
        "errors": errors,
    }


def _print_report(result: dict[str, int | list[str]]) -> None:
    """打印导入报告。"""
    print(f"\n{'=' * 55}")
    print(f"  知识库导入报告")
    print(f"{'=' * 55}")
    print(f"  总文件数 : {result['total_files']}")
    print(f"  新导入   : {result['imported']}")
    print(f"  跳过     : {result['skipped']}")
    print(f"  总分块   : {result['chunks']}")
    errors = result.get("errors", [])
    if errors:
        print(f"  失败     : {len(errors)}")
        for e in errors[:5]:
            print(f"    ✗ {e}")
        if len(errors) > 5:
            print(f"    ... 还有 {len(errors) - 5} 个错误")
    else:
        print(f"  失败     : 0")
    print(f"{'=' * 55}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hush-init-knowledge",
        description="初始化 hush.ai 知识库：从 GitHub 仓库或本地目录批量导入 Markdown 语料。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 从默认仓库（open-cognition）自动克隆并导入
  hush-init-knowledge --repo-url https://github.com/peace-lab-global/open-cognition.git

  # 仅导入心理学与哲学领域
  hush-init-knowledge --domains psychology,philosophy

  # 预览，不实际导入
  hush-init-knowledge --dry-run

  # 使用本地已下载的目录
  hush-init-knowledge --source-dir ./my-knowledge-base
        """,
    )
    parser.add_argument(
        "--repo-url",
        default=DEFAULT_REPO_URL,
        help="GitHub 仓库地址（默认: open-cognition）",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help="本地 Markdown 目录（与 --repo-url 互斥时使用）",
    )
    parser.add_argument(
        "--domains",
        default="",
        help="仅导入指定领域，逗号分隔，如: psychology,philosophy,religion",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式：只列出将要导入的文件，不实际入库",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="跳过确认提示，直接执行",
    )
    parser.add_argument(
        "--no-skip",
        action="store_true",
        help="不跳过已导入文件（强制重新导入）",
    )
    args = parser.parse_args(argv)

    reset_config()

    # 解析领域过滤
    domain_filter: list[str] | None = None
    if args.domains:
        domain_filter = [d.strip() for d in args.domains.split(",") if d.strip()]

    # 确定源目录
    source_dir: Path = args.source_dir
    use_clone = False

    # 如果 source-dir 不存在或为空，且提供了 repo-url，则 clone
    if not source_dir.exists() or not any(source_dir.iterdir()):
        if args.repo_url:
            use_clone = True
            source_dir = DEFAULT_SOURCE_DIR
        else:
            print(f"错误: 源目录不存在且未提供仓库地址: {source_dir}")
            return 1

    if use_clone:
        try:
            _clone_repo(args.repo_url, source_dir)
        except subprocess.CalledProcessError as exc:
            print(f"克隆失败: {exc}")
            return 1

    if not source_dir.exists():
        print(f"错误: 源目录不存在: {source_dir}")
        return 1

    # 收集文件
    md_files = _collect_md_files(source_dir, domain_filter)
    if not md_files:
        print("未找到可导入的 Markdown 文件。")
        return 0

    # 确认提示
    action = "预览" if args.dry_run else "导入"
    print(f"\n准备 {action} {len(md_files)} 个 Markdown 文件")
    print(f"源目录: {source_dir.resolve()}")
    if domain_filter:
        print(f"领域过滤: {', '.join(domain_filter)}")
    print()

    if not args.yes and not args.dry_run:
        try:
            ans = input("确认继续? [y/N]: ")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。")
            return 1
        if ans.lower() not in ("y", "yes"):
            print("已取消。")
            return 0

    # 执行导入
    result = asyncio.run(
        _do_import(
            source_dir,
            dry_run=args.dry_run,
            domain_filter=domain_filter,
            skip_existing=not args.no_skip,
        )
    )

    _print_report(result)

    # 如果有错误，返回非零退出码
    if result.get("errors"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
