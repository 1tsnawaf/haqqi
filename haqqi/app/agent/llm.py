"""
Thin LLM wrapper. Wired for OpenAI; falls back to a deterministic MOCK when no
provider/key is configured so the skeleton always runs.

Exposes two helpers the agent uses:
  - complete(system, user)        -> free text
  - complete_json(system, user)   -> a parsed dict (model asked for JSON)
"""
import json

from app import config

_client = None


def _openai():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def complete(system: str, user: str, temperature: float = 0.3) -> str:
    """Return the model's text response for a single-turn prompt."""
    provider = config.LLM_PROVIDER

    if provider == "openai":
        resp = _openai().chat.completions.create(
            model=config.LLM_MODEL or "gpt-4o",
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content.strip()

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=config.LLM_MODEL or "claude-sonnet-4-6",
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text.strip()

    # mock
    return (
        "[MOCK LLM] Based on the law passages provided, here is a plain-language "
        "explanation of your rights. Set LLM_PROVIDER=openai and OPENAI_API_KEY in "
        ".env to use a real model."
    )


def complete_json(system: str, user: str, temperature: float = 0.0) -> dict:
    """Return a parsed JSON object. Used for structured extraction/analysis."""
    provider = config.LLM_PROVIDER

    if provider == "openai":
        resp = _openai().chat.completions.create(
            model=config.LLM_MODEL or "gpt-4o",
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return _safe_load(resp.choices[0].message.content)

    if provider == "anthropic":
        # Anthropic has no JSON mode; ask for JSON and parse defensively.
        raw = complete(system + "\n\nRespond with ONLY valid JSON.", user)
        return _safe_load(raw)

    # mock — empty structure so callers degrade gracefully
    return {}


def _safe_load(raw: str) -> dict:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Try to salvage a JSON object embedded in prose.
        start, end = raw.find("{"), raw.rfind("}")
        if 0 <= start < end:
            try:
                return json.loads(raw[start:end + 1])
            except json.JSONDecodeError:
                pass
        return {}
