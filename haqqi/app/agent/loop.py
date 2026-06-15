"""
The bounded agent loop:  understand -> retrieve -> evaluate -> (ask) -> deliver.
Capped at MAX_CLARIFYING_QUESTIONS so it never wanders. Owned by P1.

This ships as a minimal *walking skeleton*: it retrieves, calls the (mock) LLM,
and returns a cited answer. Layer the three behaviors on top in Day 2.
"""
from app import config
from app.schemas import ChatRequest, AgentResponse, Profile
from app.agent import prompts, tools
from app.agent.llm import complete


def run(req: ChatRequest) -> AgentResponse:
    profile: Profile = req.profile

    # 1. RETRIEVE — ground the answer in the law (P2's tool)
    citations = tools.tool_search_law(req.message)

    # 2. EVALUATE — let the LLM reason over the retrieved passages
    law_context = "\n\n".join(f"[{c.article_ref}] {c.text}" for c in citations)
    user_block = f"User situation:\n{req.message}\n\nRelevant law:\n{law_context}"
    reply = complete(prompts.SYSTEM_PROMPT, user_block)

    # 3. TODO (P1): clause X-ray, rights radar, decide whether to ask_user, draft battle plan.
    #    Update `profile` as facts are learned so the UI case-file card reflects it.

    return AgentResponse(
        reply=reply,
        profile=profile,
        citations=citations,
        needs_user_input=False,
    )
