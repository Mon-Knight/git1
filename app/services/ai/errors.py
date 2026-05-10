"""
AI World Engine - Shared Error Mapping for AI Services.
Maps HTTP status codes and exceptions to user-friendly error dicts.
"""

from typing import Dict, Any


def _error(code: str, message: str, status_code: int = None, detail: str = "") -> Dict[str, Any]:
    """Standard error dict."""
    err: Dict[str, Any] = {"code": code, "message": message}
    if status_code is not None:
        err["status_code"] = status_code
    if detail:
        err["detail"] = detail
    return err


def map_http_error(status_code: int, body: str = "") -> Dict[str, Any]:
    """Map an HTTP status code to a friendly error dict."""
    mapping = {
        401: ("invalid_api_key", "API Key 无效，请检查密钥是否填写正确。"),
        402: ("insufficient_quota", "账户余额不足或额度已用尽，请检查模型服务账户余额。"),
        404: ("model_not_found_or_endpoint_error", "模型不存在，或 Base URL 地址不正确。请检查模型名称和接口地址。"),
        422: ("invalid_request", "请求参数不符合接口要求，请检查模型名称、max_tokens 或 temperature 设置。"),
        429: ("rate_limited", "请求过于频繁，已被模型服务限流，请稍后重试。"),
        500: ("server_error", "模型服务出现内部错误，请稍后重试。"),
        502: ("bad_gateway", "模型服务网关错误，请稍后重试。"),
        503: ("service_unavailable", "模型服务暂不可用，请稍后重试。"),
        504: ("gateway_timeout", "模型服务响应超时，请稍后重试。"),
    }
    code, msg = mapping.get(status_code, ("unknown_error", "发生未知错误，请查看详细信息。"))
    return _error(code, msg, status_code=status_code, detail=body[:500])


def map_exception(exc: Exception) -> Dict[str, Any]:
    """Map a caught exception to a friendly error dict."""
    import requests
    if isinstance(exc, requests.exceptions.Timeout):
        return _error("request_timeout", "请求超时，请检查网络、Base URL，或适当增加超时时间。", detail=str(exc)[:300])
    if isinstance(exc, requests.exceptions.ConnectionError):
        return _error("connection_error", "无法连接到模型服务，请检查网络和 Base URL。", detail=str(exc)[:300])
    return _error("unknown_error", "发生未知错误，请查看详细信息。", detail=str(exc)[:300])
