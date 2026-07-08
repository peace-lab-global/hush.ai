"""系统设置页面。"""

from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from hushai.meditation.admin.auth import get_admin_from_request
from hushai.meditation.admin.pages._shared import login_redirect, templates
from hushai.meditation.config import get_config

router = APIRouter(tags=["admin-web"])


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    success: str | None = None,
    error: str | None = None,
):
    """系统设置页面。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    config = get_config()

    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "admin_user": admin_user,
            "config": config,
            "success": success,
            "error": error,
        },
    )


@router.post("/settings")
async def settings_update(
    request: Request,
    default_llm_provider: str = Form(...),
    default_llm_model: str = Form(...),
    memory_top_k: int = Form(...),
    knowledge_top_k: int = Form(...),
    conversation_max_turns: int = Form(...),
    openai_api_key: str = Form(""),
    openai_base_url: str = Form(""),
    deepseek_api_key: str = Form(""),
    deepseek_base_url: str = Form(""),
    deepseek_model: str = Form(""),
    zhipu_api_key: str = Form(""),
    zhipu_base_url: str = Form(""),
    zhipu_model: str = Form(""),
    kimi_api_key: str = Form(""),
    kimi_base_url: str = Form(""),
    kimi_model: str = Form(""),
    save_remote_sources: str = Form(""),
    coze_api_base: str = Form(""),
    coze_api_token: str = Form(""),
    coze_dataset_id: str = Form(""),
    ima_urls: str = Form(""),
    coze_urls: str = Form(""),
):
    """更新系统设置。"""
    admin_user = get_admin_from_request(request)
    if not admin_user:
        return login_redirect()

    from dataclasses import replace

    from hushai.meditation.config import set_config

    old_cfg = get_config()
    try:
        # 构建远程知识源配置
        remote_sources: dict[str, dict[str, str]] = dict(old_cfg.remote_knowledge_sources)

        if bool(save_remote_sources):
            if coze_api_token.strip() or coze_dataset_id.strip():
                remote_sources["coze"] = {
                    "type": "coze",
                    "api_base": coze_api_base.strip() or "https://api.coze.cn",
                    "api_token": coze_api_token.strip(),
                    "dataset_id": coze_dataset_id.strip(),
                }
            if ima_urls.strip():
                remote_sources["ima"] = {
                    "type": "ima",
                    "urls": ima_urls.strip(),
                }
            if coze_urls.strip():
                remote_sources["coze_url"] = {
                    "type": "url",
                    "urls": coze_urls.strip(),
                }

        new_cfg = replace(
            old_cfg,
            default_llm_provider=default_llm_provider,
            default_llm_model=default_llm_model,
            memory_top_k=memory_top_k,
            knowledge_top_k=knowledge_top_k,
            conversation_max_turns=conversation_max_turns,
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            deepseek_api_key=deepseek_api_key,
            deepseek_base_url=deepseek_base_url,
            deepseek_model=deepseek_model,
            zhipu_api_key=zhipu_api_key,
            zhipu_base_url=zhipu_base_url,
            zhipu_model=zhipu_model,
            kimi_api_key=kimi_api_key,
            kimi_base_url=kimi_base_url,
            kimi_model=kimi_model,
            remote_knowledge_sources=remote_sources,
        )
        set_config(new_cfg)
        return RedirectResponse(url="/admin/settings?success=设置已更新", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/admin/settings?error=更新失败: {e}", status_code=303)
