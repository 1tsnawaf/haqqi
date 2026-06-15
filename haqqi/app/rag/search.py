"""
search_law: the agent's retrieval tool. Owned by P2.

Ships as a MOCK so the skeleton runs. Replace the mock body with a real query
once ingest.py + store.py are populated.
"""
from app import config
from app.schemas import Citation
from app.rag.store import store


def search_law(query: str, k: int = None) -> list[Citation]:
    k = k or config.TOP_K
    hits = store.query(query, k=k)
    if hits:
        return hits

    # --- MOCK fallback (walking skeleton) ---
    return [
        Citation(
            article_ref="Article XX (placeholder)",
            text=("Placeholder passage. Load the verified Saudi Labor Law into "
                  "data/labor_law/ and run `python -m app.rag.ingest`."),
        )
    ]
