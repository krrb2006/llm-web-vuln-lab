"""Thin OpenAI-compatible client used to confirm static candidates with the user's key."""

from __future__ import annotations

import json
import re

import httpx

from ..config import get_settings

settings = get_settings()

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com",
    "moonshot": "https://api.moonshot.cn/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "custom": "",
}

SYSTEM_PROMPT = """你是一名资深应用安全审计工程师，正在复核静态扫描给出的“候选问题”。
要求：
1. 只根据给出的代码片段与上下文判断，不要臆造未出现的代码。
2. 如果证据不足，verdict 必须是 uncertain，不要猜测。
3. 严格输出 JSON，不要 Markdown、不要解释性前后缀。
JSON 字段：
{"verdict":"vulnerable|safe|uncertain","severity":"critical|high|medium|low|info","title":"不超过40字的中文标题","explanation":"为什么成立/不成立，指出数据流","remediation":"具体修复方案","confidence":0-100}
"""


class LLMError(RuntimeError):
    pass


def _completion_url(provider: str, base_url: str | None) -> str:
    """Build one OpenAI-compatible chat-completions URL.

    DeepSeek's current official endpoint uses ``https://api.deepseek.com``
    without the OpenAI ``/v1`` prefix. Keep accepting the old value so keys
    saved by earlier versions of the web UI do not keep producing a 404.
    """
    base = (base_url or DEFAULT_BASE_URLS.get(provider, "")).strip().rstrip("/")
    if not base:
        raise LLMError("未配置可用的模型服务地址")
    if provider == "deepseek" and base.lower() == "https://api.deepseek.com/v1":
        base = "https://api.deepseek.com"
    if base.lower().endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def _error_detail(response: httpx.Response) -> str:
    """Keep useful provider error text instead of displaying a blank 404."""
    try:
        body = response.json()
    except ValueError:
        return response.text[:300].strip()
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            for key in ("message", "detail", "code"):
                value = error.get(key)
                if value:
                    return str(value)[:300]
        elif isinstance(error, str) and error.strip():
            return error.strip()[:300]
        for key in ("detail", "message"):
            value = body.get(key)
            if value:
                return str(value)[:300]
    return response.text[:300].strip()


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise LLMError("模型未返回 JSON")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as error:
            raise LLMError(f"模型 JSON 解析失败: {error}") from error


def _message_text(content: object) -> str:
    """Normalize both plain strings and OpenAI-compatible content-part arrays."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                parts.append(part["text"])
        return "\n".join(parts)
    return str(content)


def confirm_candidate(
    *,
    api_key: str,
    provider: str,
    base_url: str | None,
    model: str,
    file_path: str,
    language: str,
    category: str,
    rule_title: str,
    snippet: str,
    flow_text: str = "",
) -> dict:
    endpoint = _completion_url(provider, base_url)
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"文件：{file_path}\n语言：{language}\n静态规则：{category} / {rule_title}\n\n"
                    f"代码片段（含上下文）：\n```{language.lower()}\n{snippet[:4000]}\n```"
                    + (f"\n\n静态数据流路径：\n{flow_text}" if flow_text else "")
                ),
            },
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(endpoint, json=payload, headers=headers)
    except httpx.HTTPError as error:
        raise LLMError(f"模型服务连接失败: {type(error).__name__}") from error

    if response.status_code >= 400:
        detail = _error_detail(response)
        suffix = f": {detail}" if detail else ""
        raise LLMError(f"模型服务返回 {response.status_code}{suffix}")

    try:
        content = response.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as error:
        raise LLMError("模型响应结构异常") from error

    data = _extract_json(_message_text(content))
    verdict = str(data.get("verdict", "uncertain")).lower()
    if verdict not in {"vulnerable", "safe", "uncertain"}:
        verdict = "uncertain"
    severity = str(data.get("severity", "medium")).lower()
    if severity not in {"critical", "high", "medium", "low", "info"}:
        severity = "medium"
    try:
        confidence = int(data.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0
    return {
        "verdict": verdict,
        "severity": severity,
        "title": str(data.get("title", rule_title))[:180],
        "explanation": str(data.get("explanation", "")),
        "remediation": str(data.get("remediation", "")),
        "confidence": max(0, min(100, confidence)),
    }
