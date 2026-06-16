"""
Embedding helper. Wraps the OpenAI embeddings API.

Kept tiny on purpose: one batch function. If no key is configured the caller
(ingest / store) falls back to keyword search, so this never hard-blocks the app.
"""
from app import config

_client = None


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


def available() -> bool:
    """True if we can embed (OpenAI key present)."""
    return config.LLM_PROVIDER == "openai" and bool(config.OPENAI_API_KEY)


# text-embedding-3-* accepts up to 8191 tokens/input; keep well under that and
# cap request size so a 400-article corpus embeds without hitting limits.
_MAX_CHARS = 8000
_BATCH = 100


def embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts (auto-batched). Returns one vector per input."""
    client = _get_client()
    prepared = [(t or " ")[:_MAX_CHARS] for t in texts]
    vectors: list[list[float]] = []
    for i in range(0, len(prepared), _BATCH):
        resp = client.embeddings.create(model=config.EMBED_MODEL,
                                        input=prepared[i:i + _BATCH])
        vectors.extend(d.embedding for d in resp.data)
    return vectors


def embed_one(text: str) -> list[float]:
    return embed([text])[0]
