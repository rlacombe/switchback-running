"""Native provider adapters for UltraBench's common tool-calling contract.

Each adapter uses the provider's public HTTPS API directly.  The benchmark owns
the conversation loop and mock tools so a provider routing layer cannot change
the experimental condition.
"""

from __future__ import annotations

import json
import os
import asyncio
import hashlib
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class Completion:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    native_message: Any = None
    usage: dict[str, int] = field(default_factory=dict)
    response_metadata: dict[str, Any] = field(default_factory=dict)


class DirectProvider:
    name: str

    async def complete(
        self,
        *,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        reasoning: str | int | None = None,
        json_mode: bool = False,
        seed: int | None = None,
    ) -> Completion:
        raise NotImplementedError

    def append_tool_results(self, messages: list[dict[str, Any]], completion: Completion, results: list[dict[str, Any]]) -> None:
        raise NotImplementedError


def _key(variable: str) -> str:
    value = os.environ.get(variable)
    if not value:
        raise RuntimeError(f"{variable} is required for this provider.")
    return value


async def post_with_retries(client: Any, endpoint: str, **kwargs: Any) -> Any:
    import httpx

    retryable_statuses = {429, 500, 502, 503, 504}
    for attempt in range(6):
        try:
            response = await client.post(endpoint, **kwargs)
            if response.status_code not in retryable_statuses or attempt == 5:
                return response
        except httpx.TransportError:
            if attempt == 5:
                raise
        await asyncio.sleep(2 ** attempt)
    raise RuntimeError("Provider request exhausted its retry budget.")


USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "uncached_input_tokens",
    "output_tokens",
    "thinking_tokens",
    "visible_output_tokens",
)


def empty_usage() -> dict[str, int]:
    return {name: 0 for name in USAGE_FIELDS}


def add_usage(total: dict[str, int], increment: dict[str, int]) -> None:
    for name in USAGE_FIELDS:
        total[name] = total.get(name, 0) + increment.get(name, 0)


def normalize_message_content(content: Any, provider: str) -> Any:
    """Translate shared text blocks into each provider's wire format."""
    if not isinstance(content, list):
        return content
    if provider == "anthropic":
        return content
    if provider == "openai":
        return [
            {"type": "text", "text": block["text"]}
            for block in content
            if block.get("type") == "text"
        ]
    if provider == "google":
        return [
            {"text": block["text"]}
            for block in content
            if block.get("type") == "text"
        ]
    raise ValueError(f"Unsupported provider content format: {provider}")


def normalize_messages(messages: list[dict[str, Any]], provider: str) -> list[dict[str, Any]]:
    return [
        {**message, "content": normalize_message_content(message.get("content"), provider)}
        for message in messages
    ]


def prompt_cache_key(messages: list[dict[str, Any]]) -> str | None:
    cached_prefixes = []
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        cached_prefixes.extend(
            block["text"]
            for block in content
            if block.get("type") == "text" and block.get("cache_control")
        )
    if not cached_prefixes:
        return None
    digest = hashlib.sha256("\n".join(cached_prefixes).encode()).hexdigest()[:32]
    return f"ultrabench-judge-{digest}"


def openai_usage(value: dict[str, Any] | None) -> dict[str, int]:
    value = value or {}
    input_tokens = int(value.get("prompt_tokens", 0) or 0)
    output_tokens = int(value.get("completion_tokens", 0) or 0)
    cached = int((value.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0)
    thinking = int((value.get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0)
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": 0,
        "uncached_input_tokens": max(0, input_tokens - cached),
        "output_tokens": output_tokens,
        "thinking_tokens": thinking,
        "visible_output_tokens": max(0, output_tokens - thinking),
    }


def anthropic_usage(value: dict[str, Any] | None) -> dict[str, int]:
    value = value or {}
    uncached = int(value.get("input_tokens", 0) or 0)
    cached = int(value.get("cache_read_input_tokens", 0) or 0)
    cache_write = int(value.get("cache_creation_input_tokens", 0) or 0)
    output = int(value.get("output_tokens", 0) or 0)
    return {
        "input_tokens": uncached + cached + cache_write,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": cache_write,
        "uncached_input_tokens": uncached,
        "output_tokens": output,
        "thinking_tokens": 0,
        "visible_output_tokens": output,
    }


def google_usage(value: dict[str, Any] | None) -> dict[str, int]:
    value = value or {}
    input_tokens = int(value.get("promptTokenCount", 0) or 0)
    cached = int(value.get("cachedContentTokenCount", 0) or 0)
    visible = int(value.get("candidatesTokenCount", 0) or 0)
    thinking = int(value.get("thoughtsTokenCount", 0) or 0)
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": 0,
        "uncached_input_tokens": max(0, input_tokens - cached),
        "output_tokens": visible + thinking,
        "thinking_tokens": thinking,
        "visible_output_tokens": visible,
    }


class OpenAIProvider(DirectProvider):
    name = "openai"
    endpoint = "https://api.openai.com/v1/chat/completions"

    async def complete(self, *, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, reasoning: str | int | None = None, json_mode: bool = False, seed: int | None = None) -> Completion:
        import httpx

        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "system", "content": system}, *normalize_messages(messages, self.name)],
            "max_completion_tokens": 4096,
        }
        cache_key = prompt_cache_key(messages)
        if cache_key:
            payload["prompt_cache_key"] = cache_key
        if not model.startswith("gpt-5"):
            payload["temperature"] = 0
        if tools:
            payload.update({"tools": tools, "tool_choice": "auto"})
        if seed is not None:
            payload["seed"] = seed
        if isinstance(reasoning, str) and reasoning != "off":
            payload["reasoning_effort"] = reasoning
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await post_with_retries(client, self.endpoint, headers={"Authorization": f"Bearer {_key('OPENAI_API_KEY')}"}, json=payload)
            if response.is_error:
                raise RuntimeError(f"OpenAI API request failed ({response.status_code}): {response.text[:1000]}")
            body = response.json()
        message = body["choices"][0]["message"]
        calls = [ToolCall(call["id"], call["function"]["name"], json.loads(call["function"].get("arguments") or "{}")) for call in message.get("tool_calls", [])]
        metadata = {key: body.get(key) for key in ("id", "model", "system_fingerprint") if body.get(key) is not None}
        return Completion((message.get("content") or "").strip(), calls, message, openai_usage(body.get("usage")), metadata)

    def append_tool_results(self, messages: list[dict[str, Any]], completion: Completion, results: list[dict[str, Any]]) -> None:
        messages.append(completion.native_message)
        messages.extend({"role": "tool", "tool_call_id": item["id"], "content": json.dumps(item["result"])} for item in results)


class AnthropicProvider(DirectProvider):
    name = "anthropic"
    endpoint = "https://api.anthropic.com/v1/messages"

    @staticmethod
    def _tools(tools: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        return [{"name": tool["function"]["name"], "description": tool["function"]["description"], "input_schema": tool["function"]["parameters"]} for tool in tools or []]

    async def complete(self, *, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, reasoning: str | int | None = None, json_mode: bool = False, seed: int | None = None) -> Completion:
        import httpx

        payload: dict[str, Any] = {
            "model": model,
            "system": system,
            "messages": normalize_messages(messages, self.name),
            "max_tokens": 4096,
        }
        if model in {"claude-sonnet-5", "claude-opus-5"}:
            payload["max_tokens"] = 8192
            payload["thinking"] = {"type": "adaptive"}
            payload["output_config"] = {"effort": reasoning if isinstance(reasoning, str) and reasoning != "off" else "low"}
        else:
            payload["temperature"] = 0
        if tools:
            payload["tools"] = self._tools(tools)
        if isinstance(reasoning, int):
            payload["thinking"] = {"type": "enabled", "budget_tokens": max(1024, reasoning)}
            payload.pop("temperature")
        async with httpx.AsyncClient(timeout=120) as client:
            response = await post_with_retries(
                client,
                self.endpoint,
                headers={
                    "x-api-key": _key("ANTHROPIC_API_KEY"),
                    "anthropic-version": "2023-06-01",
                    "anthropic-beta": "extended-cache-ttl-2025-04-11",
                    "content-type": "application/json",
                },
                json=payload,
            )
            if response.is_error:
                raise RuntimeError(f"Anthropic API request failed ({response.status_code}): {response.text[:1000]}")
            body = response.json()
        blocks = body.get("content", [])
        calls = [ToolCall(block["id"], block["name"], block["input"]) for block in blocks if block.get("type") == "tool_use"]
        text = "".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        metadata = {key: body.get(key) for key in ("id", "model", "stop_reason", "stop_sequence") if body.get(key) is not None}
        return Completion(text, calls, blocks, anthropic_usage(body.get("usage")), metadata)

    def append_tool_results(self, messages: list[dict[str, Any]], completion: Completion, results: list[dict[str, Any]]) -> None:
        messages.append({"role": "assistant", "content": completion.native_message})
        messages.append({"role": "user", "content": [{"type": "tool_result", "tool_use_id": item["id"], "content": json.dumps(item["result"])} for item in results]})


class GoogleProvider(DirectProvider):
    name = "google"

    @staticmethod
    def _contents(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        contents = []
        for message in messages:
            role = "model" if message["role"] == "assistant" else "user"
            if message["role"] == "tool":
                results = [{"name": message["name"], "result": message["result"]}, *message.get("additional_results", [])]
                parts = [
                    {"functionResponse": {"name": item["name"], "response": {"result": item["result"]}}}
                    for item in results
                ]
                contents.append({"role": "user", "parts": parts})
            elif isinstance(message["content"], list):
                contents.append({"role": role, "parts": message["content"]})
            else:
                contents.append({"role": role, "parts": [{"text": message["content"]}]})
        return contents

    async def complete(self, *, model: str, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None, reasoning: str | int | None = None, json_mode: bool = False, seed: int | None = None) -> Completion:
        import httpx

        payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": self._contents(normalize_messages(messages, self.name)),
            "generationConfig": {"maxOutputTokens": 4096},
        }
        if not model.startswith(("gemini-3", "gemini-4")):
            payload["generationConfig"]["temperature"] = 0
        if tools:
            payload["tools"] = [{"functionDeclarations": [tool["function"] for tool in tools]}]
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        if reasoning is not None:
            if isinstance(reasoning, int):
                payload["generationConfig"]["thinkingConfig"] = {"thinkingBudget": reasoning}
            elif reasoning == "off":
                # Gemini 3 exposes a minimum thinking level rather than a true
                # off switch; Gemini 2.5 accepts a numeric budget of zero.
                payload["generationConfig"]["thinkingConfig"] = (
                    {"thinkingBudget": 0} if model.startswith("gemini-2.5") else {"thinkingLevel": "MINIMAL"}
                )
            else:
                payload["generationConfig"]["thinkingConfig"] = {"thinkingLevel": reasoning.upper()}
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        async with httpx.AsyncClient(timeout=120) as client:
            response = await post_with_retries(client, endpoint, headers={"x-goog-api-key": _key("GEMINI_API_KEY")}, json=payload)
            if response.is_error:
                raise RuntimeError(f"Gemini API request failed ({response.status_code}): {response.text[:1000]}")
            body = response.json()
        parts = body["candidates"][0]["content"].get("parts", [])
        calls = [ToolCall(f"google-call-{index}", part["functionCall"]["name"], part["functionCall"].get("args", {})) for index, part in enumerate(parts) if "functionCall" in part]
        text = "".join(part.get("text", "") for part in parts).strip()
        metadata = {key: body.get(key) for key in ("responseId", "modelVersion") if body.get(key) is not None}
        return Completion(text, calls, parts, google_usage(body.get("usageMetadata")), metadata)

    def append_tool_results(self, messages: list[dict[str, Any]], completion: Completion, results: list[dict[str, Any]]) -> None:
        messages.append({"role": "assistant", "content": completion.native_message})
        messages.append({"role": "tool", "name": results[0]["name"], "result": results[0]["result"], "additional_results": results[1:]})


def provider_for(name: str) -> DirectProvider:
    providers = {"openai": OpenAIProvider, "anthropic": AnthropicProvider, "google": GoogleProvider}
    try:
        return providers[name]()
    except KeyError as exc:
        raise ValueError(f"Unsupported provider {name!r}; use openai, anthropic, or google.") from exc
