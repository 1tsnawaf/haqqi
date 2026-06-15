"""
Contract X-ray — the signature behavior.
Audit a contract clause-by-clause; flag terms that violate or waive the user's
rights, each with a citation. Owned by P1.
"""
from app.schemas import FlaggedClause, Citation
from app.rag.search import search_law


def xray_contract(contract_text: str) -> list[FlaggedClause]:
    """
    TODO (P1):
      1. Split the contract into clauses.
      2. For each clause, retrieve the relevant law (search_law) and ask the LLM:
         does this clause conflict with or unlawfully waive a protected right?
      3. Return FlaggedClause for each problem, with its citation.
    """
    return []  # mock: nothing flagged yet
