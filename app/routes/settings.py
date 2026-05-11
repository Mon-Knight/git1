"""
AI World Engine - Settings Routes
AI configuration page and connection test.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.settings_service import SettingsService
from app.config import settings

router = APIRouter(prefix="/settings")

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Maps setting keys to form field names
SETTING_KEYS = [
    "ai_provider",
    "ai_enable_live",
    "ai_base_url",
    "ai_model",
    "ai_api_key",
    "ai_temperature",
    "ai_max_tokens",
    "ai_timeout",
    "ai_simulation_model",
    "ai_check_model",
    "ai_summary_model",
]


@router.get("/ai", response_class=HTMLResponse)
async def ai_settings_page(request: Request, db: Session = Depends(get_db)):
    """Show the AI settings page."""
    # Ensure defaults exist
    SettingsService.init_defaults(db)

    current = SettingsService.get_all(db)  # masked secrets
    config = SettingsService.get_effective_config(db)
    is_live = SettingsService.is_live_enabled(db)

    from app.services.app_settings_service import AppSettingsService
    app_settings = AppSettingsService.get_all(db)
    is_desktop = AppSettingsService.is_desktop_mode()

    return templates.TemplateResponse(request, "settings/ai.html", {
        "current": current,
        "config": config,
        "is_live": is_live,
        "errors": {},
        "success": None,
        "test_result": None,
        "active_nav": "settings",
        "app_version": settings.VERSION,
        "app_settings": app_settings,
        "is_desktop_mode": is_desktop,
    })


@router.post("/ai", response_class=HTMLResponse)
async def save_ai_settings(
    request: Request,
    db: Session = Depends(get_db),
    ai_provider: str = Form(default="mock"),
    ai_enable_live: str = Form(default=""),
    ai_base_url: str = Form(default=""),
    ai_model: str = Form(default=""),
    ai_api_key: str = Form(default=""),
    ai_temperature: str = Form(default="0.7"),
    ai_max_tokens: str = Form(default="2000"),
    ai_timeout: str = Form(default="60"),
    ai_simulation_model: str = Form(default=""),
    ai_check_model: str = Form(default=""),
    ai_summary_model: str = Form(default=""),
    action: str = Form(default="save"),
):
    """Save AI settings or restore Mock mode."""
    SettingsService.init_defaults(db)

    # Handle "restore mock" action
    if action == "restore_mock":
        SettingsService.restore_mock(db)
        current = SettingsService.get_all(db)
        config = SettingsService.get_effective_config(db)
        return templates.TemplateResponse(request, "settings/ai.html", {
            "current": current,
            "config": config,
            "is_live": False,
            "errors": {},
            "success": "已恢复 Mock AI 模式。",
            "test_result": None,
            "active_nav": "settings",
            "app_version": settings.VERSION,
        })

    # Validate
    errors = {}
    try:
        temp = float(ai_temperature)
        if temp < 0 or temp > 2:
            errors["ai_temperature"] = "Temperature 必须在 0 到 2 之间"
    except ValueError:
        errors["ai_temperature"] = "Temperature 必须是数字"

    try:
        mt = int(ai_max_tokens)
        if mt < 256 or mt > 32000:
            errors["ai_max_tokens"] = "Max Tokens 必须在 256 到 32000 之间"
    except ValueError:
        errors["ai_max_tokens"] = "Max Tokens 必须是整数"

    try:
        to = int(ai_timeout)
        if to < 5 or to > 600:
            errors["ai_timeout"] = "Timeout 必须在 5 到 600 之间"
    except ValueError:
        errors["ai_timeout"] = "Timeout 必须是整数"

    if ai_enable_live and ai_provider == "openai_compatible":
        if not ai_base_url.strip():
            errors["ai_base_url"] = "启用真实 AI 时，Base URL 不能为空"
        if not ai_model.strip():
            errors["ai_model"] = "启用真实 AI 时，Model 不能为空"
        if not ai_api_key.strip():
            # Key not provided in the form, check if existing key exists
            existing_key = SettingsService.get(db, "ai_api_key")
            if not existing_key:
                errors["ai_api_key"] = "启用真实 AI 时，API Key 不能为空"

    if errors:
        current = SettingsService.get_all(db)
        config = SettingsService.get_effective_config(db)
        return templates.TemplateResponse(request, "settings/ai.html", {
            "current": current,
            "config": config,
            "is_live": SettingsService.is_live_enabled(db),
            "errors": errors,
            "form_data": {
                "ai_provider": ai_provider,
                "ai_enable_live": ai_enable_live,
                "ai_base_url": ai_base_url,
                "ai_model": ai_model,
                "ai_temperature": ai_temperature,
                "ai_max_tokens": ai_max_tokens,
                "ai_timeout": ai_timeout,
                "ai_simulation_model": ai_simulation_model,
                "ai_check_model": ai_check_model,
                "ai_summary_model": ai_summary_model,
            },
            "success": None,
            "test_result": None,
            "active_nav": "settings",
            "app_version": settings.VERSION,
        }, status_code=422)

    # Save settings
    settings_to_save = {
        "ai_provider": ai_provider,
        "ai_enable_live": "true" if ai_enable_live else "false",
        "ai_base_url": ai_base_url.strip(),
        "ai_model": ai_model.strip(),
        "ai_temperature": ai_temperature.strip(),
        "ai_max_tokens": ai_max_tokens.strip(),
        "ai_timeout": ai_timeout.strip(),
        "ai_simulation_model": ai_simulation_model.strip(),
        "ai_check_model": ai_check_model.strip(),
        "ai_summary_model": ai_summary_model.strip(),
    }
    # Only save key if user typed a new one (not the masked placeholder)
    if ai_api_key and not ai_api_key.startswith("*"):
        settings_to_save["ai_api_key"] = ai_api_key.strip()

    SettingsService.set_many(db, settings_to_save)

    current = SettingsService.get_all(db)
    config = SettingsService.get_effective_config(db)
    is_live = SettingsService.is_live_enabled(db)

    return templates.TemplateResponse(request, "settings/ai.html", {
        "current": current,
        "config": config,
        "is_live": is_live,
        "errors": {},
        "success": "配置已保存。",
        "test_result": None,
        "active_nav": "settings",
        "app_version": settings.VERSION,
    })


@router.post("/ai/test", response_class=HTMLResponse)
async def test_ai_connection(
    request: Request,
    db: Session = Depends(get_db),
):
    """Test the current AI connection."""
    SettingsService.init_defaults(db)

    from app.services.ai.model_router import ModelRouter

    try:
        client = ModelRouter.get_client(db, "connection_test")
        result = client.test_connection()
    except Exception as e:
        result = {
            "success": False,
            "message": f"测试失败: {str(e)}",
            "provider": "unknown",
            "model": "unknown",
        }

    current = SettingsService.get_all(db)
    config = SettingsService.get_effective_config(db)
    is_live = SettingsService.is_live_enabled(db)

    return templates.TemplateResponse(request, "settings/ai.html", {
        "current": current,
        "config": config,
        "is_live": is_live,
        "errors": {},
        "success": None,
        "test_result": {
            "success": result.get("success", False),
            "message": result.get("message", "未知结果"),
            "provider": result.get("provider", "unknown"),
            "model": result.get("model", "unknown"),
        },
        "active_nav": "settings",
        "app_version": settings.VERSION,
    })


@router.post("/app", response_class=HTMLResponse)
async def save_app_settings(
    request: Request,
    db: Session = Depends(get_db),
    sidebar_expanded: str = Form(default=""),
    compact_mode: str = Form(default=""),
    desktop_width: str = Form(default=""),
    desktop_height: str = Form(default=""),
    export_default_dir: str = Form(default=""),
    settings_category: str = Form(default=""),
):
    """Save app-level settings (display, desktop, export)."""
    from app.services.app_settings_service import AppSettingsService

    success_msgs = []
    errors_list = []

    if sidebar_expanded:
        try:
            AppSettingsService.set(db, "ui_sidebar_default_expanded", sidebar_expanded)
            success_msgs.append("侧边栏默认展开设置已保存。")
        except Exception as e:
            errors_list.append(f"侧边栏设置保存失败: {e}")

    if compact_mode:
        try:
            AppSettingsService.set(db, "ui_compact_mode", compact_mode)
            success_msgs.append("紧凑模式设置已保存。")
        except Exception as e:
            errors_list.append(f"紧凑模式设置保存失败: {e}")

    if desktop_width or desktop_height:
        width = desktop_width.strip() if desktop_width else "1280"
        height = desktop_height.strip() if desktop_height else "820"
        try:
            w = int(width)
            h = int(height)
            if w < 1024 or w > 2560:
                errors_list.append("窗口宽度必须在 1024-2560 之间。")
            elif h < 700 or h > 1600:
                errors_list.append("窗口高度必须在 700-1600 之间。")
            else:
                AppSettingsService.set(db, "desktop_default_width", str(w))
                AppSettingsService.set(db, "desktop_default_height", str(h))
                AppSettingsService.save_window_size(w, h)
                success_msgs.append(f"窗口大小已保存为 {w}×{h}。将在下次启动时生效。")
        except ValueError:
            errors_list.append("窗口尺寸必须是有效数字。")

    if export_default_dir:
        dangerous = ["/etc", "/root", "C:\\Windows", "C:\\Windows\\System32", "/bin", "/sbin", "/usr/bin"]
        is_dangerous = any(export_default_dir.lower().startswith(d.lower()) for d in dangerous)
        if is_dangerous:
            errors_list.append("不允许使用系统目录作为默认导出路径。")
        else:
            try:
                AppSettingsService.set(db, "export_default_dir", export_default_dir)
                success_msgs.append("默认导出目录已保存。")
            except Exception as e:
                errors_list.append(f"导出目录设置保存失败: {e}")

    SettingsService.init_defaults(db)
    current = SettingsService.get_all(db)
    config = SettingsService.get_effective_config(db)
    is_live = SettingsService.is_live_enabled(db)
    app_settings = AppSettingsService.get_all(db)

    success = "；".join(success_msgs) if success_msgs else None
    app_errors = {("submit" if not success_msgs else ""): "；".join(errors_list)} if errors_list else {}

    return templates.TemplateResponse(request, "settings/ai.html", {
        "current": current, "config": config, "is_live": is_live,
        "errors": app_errors, "success": success, "test_result": None,
        "active_nav": "settings", "app_version": settings.VERSION,
        "app_settings": app_settings, "settings_category": settings_category,
        "is_desktop_mode": AppSettingsService.is_desktop_mode(),
    })
