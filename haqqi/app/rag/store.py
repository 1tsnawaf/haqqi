"""Vector store wrapper. Owned by P2. Swap the backend freely (Chroma/FAISS/etc.)."""
from app.schemas import Citation


class VectorStore:
    def __init__(self):
        # TODO (P2): connect/load the persisted index.
        self._ready = False

    def query(self, text: str, k: int = 4) -> list[Citation]:
        # TODO (P2): embed `text`, search, map hits -> Citation(article_ref, text).
        return []


# Singleton used by search.py
store = VectorStore()
