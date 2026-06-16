"""
search_law: the agent's retrieval tool.

Queries the persisted index (semantic if embeddings are present, else keyword),
biasing toward the primary corpus (labor_law) so employment questions stay
grounded in the labor law while civil-procedure articles still surface for
"where/how to file" questions. Falls back to a clearly-labelled placeholder only
if the index hasn't been built.
"""
from app import config
from app.schemas import Citation
from app.rag.store import store


def search_law(query: str, k: int = None, prefer_folder: str = None) -> list[Citation]:
    k = k or config.TOP_K
    hits = store.query(
        query, k=k,
        prefer_folder=config.PRIMARY_CORPUS if prefer_folder is None else prefer_folder,
        prefer_boost=config.PRIMARY_BOOST,
    )
    if hits:
        return hits

    if not store.ready:
        return [
            Citation(
                article_ref="(لم يتم بناء الفهرس)",
                text=("لا توجد قاعدة معرفة. أضف نصوص الأنظمة إلى مجلد data/ ثم نفّذ: "
                      "python -m app.rag.ingest"),
            )
        ]
    return []  # index exists but nothing matched — let the agent say it's unsure
