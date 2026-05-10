"""
AI World Engine - Test AI Client
Tests for MockAIClient and OpenAICompatibleClient using mocks.
No real network requests are made.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.services.ai.mock_client import MockAIClient
from app.services.ai.openai_compatible_client import OpenAICompatibleClient
from app.services.ai.base import success_response, error_response


# ── MockAIClient Tests ──

def test_mock_generate_success():
    """Mock client should always return a successful result."""
    client = MockAIClient()
    msg = [{"role": "user", "content": "测试推演问题"}]
    result = client.generate(msg)
    assert result["success"] is True
    assert "Mock AI" in result["content"]
    assert result["model"] == "mock"
    assert result["provider"] == "mock"
    assert result["error"] is None
    assert "usage" in result


def test_mock_test_connection():
    """Mock client test_connection should always succeed."""
    client = MockAIClient()
    result = client.test_connection()
    assert result["success"] is True
    assert "Mock AI" in result["message"]


def test_mock_provider_and_model():
    """Mock client should report correct provider/model."""
    client = MockAIClient()
    assert client.provider == "mock"
    assert client.model_name == "mock"


# ── OpenAICompatibleClient Tests ──

def _make_mock_post(status_code=200, json_data=None, text=""):
    """Create a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    return resp


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_normal_response(mock_post):
    """Should parse a valid Chat Completions response."""
    mock_post.return_value = _make_mock_post(json_data={
        "choices": [{"message": {"content": "推演结果内容"}}],
        "model": "gpt-4o",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    })
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is True
    assert result["content"] == "推演结果内容"
    assert result["provider"] == "openai_compatible"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_401_error(mock_post):
    """401 should map to invalid_api_key."""
    mock_post.return_value = _make_mock_post(status_code=401, text="Unauthorized")
    client = OpenAICompatibleClient("bad-key", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "invalid_api_key"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_402_error(mock_post):
    """402 should map to insufficient_quota."""
    mock_post.return_value = _make_mock_post(status_code=402, text="Payment required")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "insufficient_quota"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_404_error(mock_post):
    """404 should map to model_not_found_or_endpoint_error."""
    mock_post.return_value = _make_mock_post(status_code=404, text="Not found")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "bad-model")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "model_not_found_or_endpoint_error"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_422_error(mock_post):
    """422 should map to invalid_request."""
    mock_post.return_value = _make_mock_post(status_code=422, text="Validation error")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "invalid_request"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_429_error(mock_post):
    """429 should map to rate_limited."""
    mock_post.return_value = _make_mock_post(status_code=429, text="Rate limit")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "rate_limited"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_500_error(mock_post):
    """500 should map to server_error."""
    mock_post.return_value = _make_mock_post(status_code=500, text="Internal error")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "server_error"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_timeout(mock_post):
    """Timeout should map to request_timeout."""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout("timed out")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "request_timeout"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_connection_error(mock_post):
    """ConnectionError should map to connection_error."""
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("connection refused")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "connection_error"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_missing_choices(mock_post):
    """Response with no choices should return invalid_response error."""
    mock_post.return_value = _make_mock_post(json_data={"model": "gpt-4o", "usage": {}})
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "invalid_response"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_invalid_json(mock_post):
    """Non-JSON response should return invalid_response error."""
    mock_post.return_value = _make_mock_post(text="not json")
    mock_post.return_value.json.side_effect = ValueError("Expecting value")
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.generate([{"role": "user", "content": "test"}])
    assert result["success"] is False
    assert result["error"]["code"] == "invalid_response"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_key_not_in_payload(mock_post):
    """Verify API Key is not visible in the request body, only in headers."""
    mock_post.return_value = _make_mock_post(json_data={
        "choices": [{"message": {"content": "ok"}}],
        "model": "gpt-4o",
        "usage": {},
    })
    key = "sk-secret-long-key-abcd"
    client = OpenAICompatibleClient(key, "https://api.example.com/v1", "gpt-4o")
    client.generate([{"role": "user", "content": "test"}])
    call_kwargs = mock_post.call_args
    # Check body does not contain the key
    body = str(call_kwargs)
    assert key not in call_kwargs.kwargs.get("json", {}), "API Key should not appear in request body"


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_test_connection_success(mock_post):
    """test_connection should succeed when API responds normally."""
    mock_post.return_value = _make_mock_post(json_data={
        "choices": [{"message": {"content": "Hi"}}],
        "model": "gpt-4o",
        "usage": {},
    })
    client = OpenAICompatibleClient("sk-test", "https://api.example.com/v1", "gpt-4o")
    result = client.test_connection()
    assert result["success"] is True
    assert "连接成功" in result["message"]


@patch("app.services.ai.openai_compatible_client.requests.post")
def test_openai_client_test_connection_failure(mock_post):
    """test_connection should report failure on API error."""
    mock_post.return_value = _make_mock_post(status_code=401, text="Unauthorized")
    client = OpenAICompatibleClient("sk-bad", "https://api.example.com/v1", "gpt-4o")
    result = client.test_connection()
    assert result["success"] is False


# ── Error module tests ──

def test_map_http_error_unknown_status():
    """Unknown status code should map to unknown_error."""
    from app.services.ai.errors import map_http_error
    err = map_http_error(418)
    assert err["code"] == "unknown_error"


def test_map_http_error_import():
    """Errors module should be importable."""
    from app.services.ai.errors import map_http_error, map_exception
    assert callable(map_http_error)
    assert callable(map_exception)
