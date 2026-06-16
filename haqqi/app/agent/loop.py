"""
The bounded agent loop:  understand -> retrieve -> evaluate -> (ask) -> deliver.

Each turn:
  1. UNDERSTAND  — extract facts from the message, merge into the live case file.
  2. X-RAY       — if the message contains a contract, audit it clause-by-clause.
  3. RETRIEVE    — ground the question in the law (RAG).
  4. RIGHTS RADAR— proactively surface entitlements the user didn't ask about.
  5. ASK         — if a key fact is missing, ask for it (capped so it never wanders).
  6. DELIVER     — compose a cited reply, plus a battle plan once we have enough.

Owned by P1.
"""
from app import config
from app.schemas import ChatRequest, AgentResponse, Profile, Citation
from app.agent import prompts
from app.agent.llm import complete, complete_json
from app.behaviors.xray import xray_contract, looks_like_contract, retrieve_clause_law
from app.behaviors.rights_radar import find_unclaimed_rights
from app.behaviors.battle_plan import draft_action
from app.rag.search import search_law

_MONEY_WORDS = ("pay", "salary", "wage", "owed", "compensation", "end-of-service",
                "end of service", "gratuity", "money", "fired", "terminat", "resign",
                "dismiss", "راتب", "مكافأة", "فصل", "استقال")


def run(req: ChatRequest) -> AgentResponse:
    # ---- 1. UNDERSTAND: extract + merge facts into the case file ----------------
    profile = _update_profile(req.profile, req.message, req.language)

    # ---- 2 & 3. RETRIEVE (shared context) + X-RAY -------------------------------
    # The general answer and the X-ray MUST reason over the SAME retrieved law, or
    # they can contradict (Q&A says "no provision" while X-ray cites an article).
    # For a contract we union general retrieval with clause-by-clause retrieval.
    is_contract = looks_like_contract(req.message)
    citations = search_law(req.message)
    if is_contract:
        pool = {c.article_ref: c for c in citations}
        for c in retrieve_clause_law(req.message):
            pool.setdefault(c.article_ref, c)
        citations = list(pool.values())
        flagged = xray_contract(req.message, citations=citations)
    else:
        flagged = []

    # ---- 4. RIGHTS RADAR --------------------------------------------------------
    radar = find_unclaimed_rights(profile)

    # ---- 5. ASK? bounded clarifying questions -----------------------------------
    asked = int(profile.extra.get("questions_asked", 0))
    missing = _missing_facts(profile, req.message)
    needs_input = bool(missing) and asked < config.MAX_CLARIFYING_QUESTIONS
    if needs_input:
        profile.extra["questions_asked"] = asked + 1

    # ---- 6. DELIVER -------------------------------------------------------------
    reply = _compose(req, profile, citations, radar, missing if needs_input else [])

    if flagged:
        reply += "\n\n---\n### ⚠️ فحص بنود العقد\n"
        for f in flagged:
            reply += f"\n- **{f.issue}** _(بحسب {f.citation.article_ref})_\n  > {f.clause}"

    # Battle plan once we understand the situation and aren't still gathering facts.
    if not needs_input and _ready_for_plan(profile):
        plan = draft_action(profile, profile.issue or req.message, citations + radar)
        reply += "\n\n---\n### 🗂️ خطة العمل\n" + plan

    # Sources = ONLY the articles actually cited in the reply (not everything we
    # retrieved). Flagged-clause citations are always cited (in the X-ray section).
    pool = _dedupe(citations + radar + [f.citation for f in flagged])
    cited = [c for c in pool if c.article_ref in reply]

    return AgentResponse(
        reply=reply,
        profile=profile,
        citations=cited,
        flagged_clauses=flagged,
        needs_user_input=needs_input,
    )


# --------------------------------------------------------------------------------
_PROFILE_FIELDS = ("role", "tenure_years", "monthly_salary", "employment_status",
                   "issue", "contract_type", "notice_given", "termination_reason")


def _update_profile(profile: Profile, message: str, language: str) -> Profile:
    data = complete_json(prompts.EXTRACT_PROFILE, f"User message:\n{message}")
    for field in _PROFILE_FIELDS:
        val = data.get(field)
        if val not in (None, "", []):
            setattr(profile, field, val)
    profile.extra.setdefault("language", data.get("language") or language)
    return profile


def _missing_facts(profile: Profile, message: str) -> list[str]:
    """Critical facts to gather before drawing fact-dependent conclusions."""
    money_topic = any(w in message.lower() for w in _MONEY_WORDS)
    is_separation = profile.employment_status in ("terminated", "resigned")
    if not is_separation and not money_topic:
        return []

    missing = []
    if profile.tenure_years is None:
        missing.append("مدة خدمتك لدى صاحب العمل، لتقدير مكافأة نهاية الخدمة والحقوق "
                       "المرتبطة بمدة الخدمة")
    if profile.monthly_salary is None:
        missing.append("راتبك الشهري، لأن معظم المستحقات تُحسب على أساسه")

    # For a termination/resignation, compensation, notice pay, and whether the
    # dismissal was lawful all hinge on these — ask before concluding on them.
    if is_separation:
        if profile.contract_type is None:
            missing.append("هل عقدك محدد المدة (له تاريخ انتهاء) أم غير محدد المدة — "
                           "فهذا يغيّر طريقة حساب التعويض ومهلة الإشعار")
        if profile.notice_given is None:
            missing.append("هل قدّم لك صاحب العمل إشعاراً كتابياً قبل إنهاء العقد، وكم عدد أيامه")
        if profile.termination_reason is None:
            missing.append("ما السبب الذي ذُكر لإنهاء العقد — فهذا يحدد ما إذا كان الإنهاء "
                           "لسبب مشروع من عدمه، وبالتالي ما تستحقه من تعويض")
    return missing


def _ready_for_plan(profile: Profile) -> bool:
    return bool(profile.issue) and profile.employment_status in (
        "terminated", "resigned", "employed")


def _compose(req: ChatRequest, profile: Profile, citations: list[Citation],
             radar: list[Citation], questions: list[str]) -> str:
    law_block = "\n\n".join(f"[{c.article_ref}] {c.text}" for c in citations)
    radar_block = "\n".join(f"- ({c.article_ref}) {c.text}" for c in radar) or "(none)"
    q_block = "\n".join(f"- {q}" for q in questions) or "(none — do not ask questions)"
    user = (
        f"User situation:\n{req.message}\n\n"
        f"Case profile:\n{profile.model_dump_json(exclude_none=True)}\n\n"
        f"Relevant law passages:\n{law_block}\n\n"
        f"Proactive entitlements to weave in (rights radar):\n{radar_block}\n\n"
        f"Clarifying questions to ask (only these):\n{q_block}"
    )
    system = prompts.SYSTEM_PROMPT + "\n\n" + prompts.COMPOSE
    return complete(system, user)


def _dedupe(citations: list[Citation]) -> list[Citation]:
    seen, out = set(), []
    for c in citations:
        if c.article_ref not in seen:
            seen.add(c.article_ref)
            out.append(c)
    return out
