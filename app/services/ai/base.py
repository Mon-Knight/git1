"""
AI World Engine - Base AI Client Interface.
All concrete providers (Mock, OpenAI-compatible) implement this.
"""

from typing import Dict, Any, List, Optional


class AIClient:
    """Abstract AI client base class."""

    @property
    def provider(self) -> str:
        return "unknown"

    @property
    def model_name(self) -> str:
        return ""

    def generate(self, messages: List[Dict[str, str]], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a chat completion from a list of messages.

        Args:
            messages: List of {"role": "system"|"user"|"assistant", "content": "..."} dicts.
            options: Optional provider-specific options (temperature, max_tokens, timeout).

        Returns:
            {
                "success": bool,
                "content": str,          # the assistant message text
                "raw": Any | None,       # raw provider response (for debugging / saving)
                "model": str,
                "provider": str,
                "usage": {
                    "prompt_tokens": int,
                    "completion_tokens": int,
                    "total_tokens": int
                } | None,
                "error": {
                    "code": str,
                    "message": str,
                    "status_code": int | None,
                    "detail": str
                } | None
            }
        """
        raise NotImplementedError

    def test_connection(self) -> Dict[str, Any]:
        """
        Test whether the provider is reachable and configured.

        Returns:
            {
                "success": bool,
                "message": str,
                "provider": str,
                "model": str
            }
        """
        raise NotImplementedError


def success_response(
    content: str,
    raw: Any = None,
    model: str = "",
    provider: str = "",
    usage: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """Build a standard success dict."""
    return {
        "success": True,
        "content": content,
        "raw": raw,
        "model": model,
        "provider": provider,
        "usage": usage,
        "error": None,
    }


def error_response(
    error_dict: Dict[str, Any],
    model: str = "",
    provider: str = "",
) -> Dict[str, Any]:
    """Build a standard error dict."""
    return {
        "success": False,
        "content": "",
        "raw": None,
        "model": model,
        "provider": provider,
        "usage": None,
        "error": error_dict,
    }
