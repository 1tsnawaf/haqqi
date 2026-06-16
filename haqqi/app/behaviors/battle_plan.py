"""
Battle plan — turn knowledge into action.
Draft the letter / script / evidence checklist + where to file, grounded in the
rights identified for the case.
"""
from app.schemas import Profile, Citation
from app.rag.search import search_law
from app.agent import prompts
from app.agent.llm import complete
from app.behaviors.common import law_context


def draft_action(profile: Profile, issue: str, rights: list[Citation] | None = None) -> str:
    """Produce a concrete next-step plan for the user's situation."""
    citations = rights or search_law(issue or (profile.issue or "employment dispute"))
    profile_block = profile.model_dump_json(exclude_none=True)
    user = (
        f"Case profile:\n{profile_block}\n\n"
        f"Issue:\n{issue or profile.issue or '(not specified)'}\n\n"
        f"Rights / law in play:\n{law_context(citations)}"
    )
    return complete(prompts.BATTLE_PLAN, user)
