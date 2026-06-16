"""
Rights radar — proactive discovery.
Surface entitlements the user did not ask about, grounded in retrieved law.
Returns Citations whose text carries the plain-language explanation, so the loop
can both fold them into the reply and list them as sources.
"""
from app.schemas import Profile, Citation
from app.rag.search import search_law
from app.agent import prompts
from app.agent.llm import complete_json
from app.behaviors.common import law_context, citation_for


def find_unclaimed_rights(profile: Profile) -> list[Citation]:
    """Identify likely entitlements the user didn't mention."""
    # Build a retrieval query from what we know about the case.
    facts = []
    if profile.employment_status:
        facts.append(profile.employment_status)
    if profile.tenure_years:
        facts.append(f"{profile.tenure_years} years of service")
    if profile.issue:
        facts.append(profile.issue)
    query = ("employee entitlements end-of-service award unused leave payout notice "
             "period overtime final wages " + " ".join(facts))
    citations = search_law(query)

    profile_block = profile.model_dump_json(exclude_none=True)
    user = (
        f"Case profile:\n{profile_block}\n\n"
        f"Relevant law passages:\n{law_context(citations)}"
    )
    data = complete_json(prompts.RIGHTS_RADAR, user)

    rights = []
    for item in data.get("rights", []):
        base = citation_for(item.get("article_ref", ""), citations)
        title = item.get("title", "").strip()
        explanation = item.get("explanation", "").strip()
        rights.append(
            Citation(
                article_ref=base.article_ref,
                text=f"{title} — {explanation}" if title else explanation,
                source=base.source,
            )
        )
    return rights
