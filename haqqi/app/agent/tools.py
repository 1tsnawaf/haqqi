"""
The agent's tools. Three is enough for a real agent — resist adding more.
Owned by P1, but search_law is backed by P2's RAG and draft_action by behaviors/.
"""
from app.schemas import Citation, Profile
from app.rag.search import search_law           # P2
from app.behaviors.battle_plan import draft_action  # battle plan


def tool_search_law(query: str) -> list[Citation]:
    """Retrieve relevant Labor Law passages (RAG). Returns citations."""
    return search_law(query)


def tool_ask_user(question: str) -> dict:
    """Signal the UI to collect a missing fact. The loop pauses here."""
    return {"action": "ask_user", "question": question}


def tool_draft_action(profile: Profile, issue: str) -> str:
    """Battle plan: produce a letter / script / evidence checklist."""
    return draft_action(profile, issue)
