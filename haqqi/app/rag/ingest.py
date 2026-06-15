"""
Build the knowledge base from the verified Labor Law text. Owned by P2.

Steps: load source text -> split into article-aware chunks -> embed -> persist.
Run once before the demo:  python -m app.rag.ingest
"""
from pathlib import Path
from app import config


def load_documents(data_dir: str = None) -> list[dict]:
    """Read raw law text files from data/labor_law/. One dict per chunk."""
    data_dir = Path(data_dir or config.LAW_DATA_DIR)
    docs = []
    for path in data_dir.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        # TODO (P2): split on article boundaries so each chunk keeps its article number,
        # which is what lets the agent cite "Article NN" accurately.
        docs.append({"text": text, "article_ref": path.stem, "source": "Saudi Labor Law"})
    return docs


def build_index():
    docs = load_documents()
    if not docs:
        print("No law text found in", config.LAW_DATA_DIR,
              "- add the verified Labor Law .txt files first.")
        return
    # TODO (P2): embed `docs` and persist to a vector store (Chroma / FAISS).
    print(f"Loaded {len(docs)} chunks. TODO: embed + persist.")


if __name__ == "__main__":
    build_index()
