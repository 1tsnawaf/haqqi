"""Shared helpers for the three behaviors."""
from app.schemas import Citation


def law_context(citations: list[Citation]) -> str:
    """Render retrieved passages for the prompt, tagged by article."""
    return "\n\n".join(f"[{c.article_ref}] {c.text}" for c in citations)


def citation_for(article_ref: str, citations: list[Citation]) -> Citation:
    """Find the retrieved Citation matching an article_ref the LLM returned.

    Guards against the model citing an article that wasn't actually retrieved:
    if there's no match we keep the ref but mark it for verification rather than
    fabricating passage text.
    """
    ref = (article_ref or "").strip().lower()
    for c in citations:
        if c.article_ref.strip().lower() == ref or ref in c.article_ref.strip().lower():
            return c
    return Citation(
        article_ref=article_ref or "(unverified)",
        text="(Citation not found in retrieved passages — verify against the official law.)",
    )
