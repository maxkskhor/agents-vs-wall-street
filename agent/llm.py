"""Thin provider layer: Anthropic + OpenAI chat calls with disk caching.

Every call is cached under cache/llm/ keyed by a hash of (provider, model,
prompt). That makes reruns free, keeps the 45-minute final-run window safe, and
lets the backtest reuse extraction work. Responses are expected to be JSON;
we strip code fences and parse defensively.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

from .config import CACHE, REPO_ROOT

_ENV_LOADED = False


def load_env() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env = REPO_ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    _ENV_LOADED = True


def available_providers() -> list[str]:
    load_env()
    out = []
    if os.environ.get("ANTHROPIC_API_KEY"):
        out.append("anthropic")
    if os.environ.get("OPENAI_API_KEY"):
        out.append("openai")
    return out


def default_model(provider: str) -> str:
    load_env()
    if provider == "anthropic":
        return os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-5"
    return os.environ.get("OPENAI_MODEL") or "gpt-5.1"


def extract_model(provider: str) -> str:
    """Cheaper model for high-volume transcription; A/B-checked against the
    default model on sample docs with identical output."""
    load_env()
    if provider == "openai":
        return os.environ.get("EXTRACT_MODEL") or "gpt-5.6-luna"
    return default_model(provider)


class LLMError(RuntimeError):
    pass


def _cache_path(provider: str, model: str, system: str, user: str) -> Path:
    h = hashlib.sha256(f"{provider}\x00{model}\x00{system}\x00{user}".encode()).hexdigest()[:32]
    d = CACHE / "llm"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{h}.json"


def chat(provider: str, system: str, user: str, model: str | None = None,
         max_tokens: int = 4000, use_cache: bool = True, temperature: float = 0.2) -> str:
    load_env()
    model = model or default_model(provider)
    cp = _cache_path(provider, model, system, user)
    if use_cache and cp.exists():
        return json.loads(cp.read_text())["text"]

    text = None
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            if provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic()
                resp = client.messages.create(
                    model=model, max_tokens=max_tokens, temperature=temperature,
                    system=system, messages=[{"role": "user", "content": user}])
                text = "".join(b.text for b in resp.content if b.type == "text")
            elif provider == "openai":
                import openai
                client = openai.OpenAI()
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": system},
                              {"role": "user", "content": user}])
                text = resp.choices[0].message.content or ""
            else:
                raise LLMError(f"unknown provider {provider}")
            break
        except Exception as e:  # noqa: BLE001 - retry then surface
            last_err = e
            time.sleep(2 * (attempt + 1))
    if text is None:
        raise LLMError(f"{provider}/{model} failed after retries: {last_err}")

    cp.write_text(json.dumps({"provider": provider, "model": model, "text": text}))
    return text


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def parse_json(text: str):
    m = _FENCE_RE.search(text)
    if m:
        text = m.group(1)
    text = text.strip()
    start = text.find("{")
    start_l = text.find("[")
    if start_l != -1 and (start == -1 or start_l < start):
        start = start_l
    if start > 0:
        text = text[start:]
    return json.loads(text)


def chat_json(provider: str, system: str, user: str, **kw):
    text = chat(provider, system, user, **kw)
    try:
        return parse_json(text)
    except json.JSONDecodeError as e:
        raise LLMError(f"{provider}: response was not valid JSON: {e}\n{text[:500]}") from e
