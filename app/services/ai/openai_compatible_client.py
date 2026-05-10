"""
AI World Engine - OpenAI-Compatible AI Client.
Supports any provider that exposes a Chat Completions API compatible with OpenAI's format.
Works with DeepSeek, MiMo Token Plan, Ollama, local models, etc.
"""

import requests
from typing import Dict, Any, List, Optional

from app.services.ai.base import AIClient, success_response, error_response
from app.services.ai.errors import map_http_error, map_exception


class OpenAICompatibleClient(AIClient):
    """Client for OpenAI-compatible Chat Completions APIs."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: int = 60,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout

    @property
    def provider(self) -> str:
        return "openai_compatible"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def _chat_url(self) -> str:
        return f"{self._base_url}/chat/completions"

    def generate(
        self,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a Chat Completions request and return a standard response."""
        opts = options or {}
        temperature = opts.get("temperature", self._temperature)
        max_tokens = opts.get("max_tokens", self._max_tokens)
        timeout = opts.get("timeout", self._timeout)
        # Allow overriding model per-request
        model = opts.get("model") or self._model

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            resp = requests.post(
                self._chat_url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.exceptions.Timeout as exc:
            err = map_exception(exc)
            return error_response(err, model=model, provider=self.provider)
        except requests.exceptions.ConnectionError as exc:
            err = map_exception(exc)
            return error_response(err, model=model, provider=self.provider)
        except Exception as exc:
            err = map_exception(exc)
            return error_response(err, model=model, provider=self.provider)

        # Non-2xx
        if resp.status_code != 200:
            err = map_http_error(resp.status_code, resp.text[:500])
            return error_response(err, model=model, provider=self.provider)

        # Parse JSON
        try:
            data = resp.json()
        except Exception:
            return error_response(
                {"code": "invalid_response", "message": "无法解析模型服务返回的 JSON。", "detail": resp.text[:300]},
                model=model,
                provider=self.provider,
            )

        # Extract content from choices
        choices = data.get("choices")
        if not choices or not isinstance(choices, list) or len(choices) == 0:
            msg = "模型返回的 JSON 中缺少 choices 字段。"
            detail = f"Response keys: {list(data.keys())}"
            return error_response(
                {"code": "invalid_response", "message": msg, "detail": detail},
                model=model,
                provider=self.provider,
            )

        content = choices[0].get("message", {}).get("content", "")
        usage_raw = data.get("usage", {})
        usage = {
            "prompt_tokens": usage_raw.get("prompt_tokens", 0),
            "completion_tokens": usage_raw.get("completion_tokens", 0),
            "total_tokens": usage_raw.get("total_tokens", 0),
        }

        return success_response(
            content=content,
            raw=data,
            model=data.get("model", model),
            provider=self.provider,
            usage=usage,
        )

    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection by sending a minimal request.
        Returns success/failure with a human-readable message.
        """
        messages = [{"role": "user", "content": "Say hi in one word."}]
        result = self.generate(messages, {"max_tokens": 10, "timeout": 15})
        if result["success"]:
            return {
                "success": True,
                "message": f"连接成功，当前模型 [{self._model}] 可用。",
                "provider": self.provider,
                "model": self._model,
            }
        else:
            err = result.get("error", {})
            return {
                "success": False,
                "message": err.get("message", "连接失败"),
                "provider": self.provider,
                "model": self._model,
            }
