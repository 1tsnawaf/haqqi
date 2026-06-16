"""
Contract X-ray — the signature behavior.
Audit a contract clause-by-clause; flag terms that violate or waive the user's
rights, each with a citation grounded in retrieved law.
"""
import re

from app.schemas import FlaggedClause, Citation
from app.rag.search import search_law
from app.agent import prompts
from app.agent.llm import complete_json
from app.behaviors.common import law_context, citation_for


_PER_CLAUSE_K = 4


def retrieve_clause_law(contract_text: str) -> list[Citation]:
    """Clause-by-clause retrieval for a contract, unioned by article.

    Each clause is searched on its own so a focused protection (e.g. the
    non-compete Article 83) is not diluted by the other clauses, plus a broad
    seed so common protections are covered even when a clause is vaguely worded.
    The loop reuses this so the general answer and the X-ray share ONE context.
    """
    by_ref: dict[str, Citation] = {}
    seed = search_law("مكافأة نهاية الخدمة الإشعار المنافسة التنازل عن الحقوق "
                      "الأجر الإضافي ساعات العمل الإضافية الإجازة إنهاء العقد")
    for c in seed:
        by_ref.setdefault(c.article_ref, c)
    for clause in split_clauses(contract_text):
        for c in search_law(clause, k=_PER_CLAUSE_K):
            by_ref.setdefault(c.article_ref, c)
    return list(by_ref.values())


def xray_contract(contract_text: str, citations: list[Citation] = None) -> list[FlaggedClause]:
    """Flag clauses that conflict with the worker's statutory rights.

    Pass `citations` to audit against an already-retrieved context (so the X-ray
    and the general answer never disagree); otherwise it retrieves its own.
    """
    if not contract_text or not contract_text.strip():
        return []

    clauses = split_clauses(contract_text)
    if citations is None:
        citations = retrieve_clause_law(contract_text)

    user = (
        "Contract clauses:\n" + "\n".join(f"- {c}" for c in clauses) + "\n\n"
        f"Relevant law passages:\n{law_context(citations)}"
    )
    data = complete_json(prompts.XRAY, user)

    flagged = []
    for item in data.get("flagged", []):
        flagged.append(
            FlaggedClause(
                clause=item.get("clause", "").strip(),
                issue=item.get("issue", "").strip(),
                citation=citation_for(item.get("article_ref", ""), citations),
            )
        )
    return flagged


# A line/segment that starts a new clause: Arabic "البند ...", English "Clause N"
# / "Article N", or a numbered item ("1.", "2)", "٣-").
_CLAUSE_SPLIT = re.compile(
    r"(?=(?:^|\n)\s*(?:البند\b|clause\s+\d|article\s+\d|[0-9٠-٩]+\s*[.)\-:]))",
    re.I,
)


def split_clauses(text: str) -> list[str]:
    """Split a contract into individual clauses for clause-by-clause retrieval."""
    parts = [p.strip() for p in _CLAUSE_SPLIT.split(text) if p and p.strip()]
    # Drop a leading preamble that carries no clause marker (e.g. a title line).
    if len(parts) > 1 and not _CLAUSE_SPLIT.match("\n" + parts[0]):
        parts = parts[1:] if len(parts[0]) < 60 else parts
    if len(parts) < 2:                    # no markers — fall back to lines/sentences
        parts = [s.strip() for s in re.split(r"[\n؛.]+", text) if len(s.strip()) >= 15]
    return parts[:20] or [text.strip()]


# Clause markers: English "Clause N", numbered items, or Arabic "البند" (which is
# followed by an ordinal WORD — "البند الأول" — not a digit).
_CLAUSE_PATTERN = re.compile(
    r"\bclause\s+\d+\b|\barticle\s+\d+\b|^\s*[0-9٠-٩]+\s*[.)]\s|البند\b", re.I | re.M)


def looks_like_contract(text: str) -> bool:
    """Heuristic: does this message contain pasted contract text to audit?

    Triggers on explicit clause markers (English or Arabic) or on enough
    contractual phrasing — independent of length, so pasting even a couple of
    clauses is X-rayed, while a short plain question is not.
    """
    if not text or len(text) < 80:
        return False
    t = text.lower()
    signals = ("clause", "agreement", "the employee", "the employer", "shall",
               "hereby", "non-compete", "noncompete", "terminat", "this contract",
               "the company agrees", "the parties",
               "بند", "يلتزم", "الطرف الأول", "الطرف الثاني", "صاحب العمل",
               "العامل", "يتعهد", "عقد العمل", "هذا العقد")
    hits = sum(s in t for s in signals)
    if _CLAUSE_PATTERN.search(text):
        return hits >= 1
    return len(text) > 180 and hits >= 2
