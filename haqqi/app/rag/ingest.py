"""
Build the knowledge base from the Arabic legal corpus.

Two corpora live under DATA_DIR, one subfolder each:
  - labor_law/        (PRIMARY — employment questions)   ~224 articles
  - civil_procedure/  (SECONDARY — where/how to file)    ~184 articles

File format (UTF-8):
  - line 1            = the law name           (e.g. "نظام العمل")
  - chapter headings  = lines starting "الباب"
  - section headings  = lines starting "الفصل"  (context only)
  - article headers   = a short line that is "المادة <ordinal words>" + optional ":"
  - "تعديلات المادة"  = amendment markers — ignored (not content)
  - article body      = everything until the next article header

One chunk per article, carrying: article_ref, chapter, source (law name), folder.
Run after any corpus change:   python -m app.rag.ingest
"""
import json
import re
from pathlib import Path

from app import config
from app.rag import embeddings

# An article header: a line consisting only of "المادة" + Arabic ordinal words,
# optionally ending with a colon. Short by construction, which separates true
# headers from in-text references that merely start a sentence.
_ARTICLE_HEADER = re.compile(r"^\s*(المادة[؀-ۿ\s]*?)\s*:?\s*$")
_AMENDMENT_MARKER = "تعديلات المادة"


def _is_article_header(line: str) -> bool:
    s = line.strip()
    if not s.startswith("المادة"):
        return False
    if len(s) > 50:                       # real designations are short
        return False
    m = _ARTICLE_HEADER.match(s)
    if not m:
        return False
    # Reject in-text references like "المادة الخامسة من هذا النظام": the words
    # after المادة must be few (an ordinal phrase), not a clause.
    rest = m.group(1).replace("المادة", "", 1).split()
    return 1 <= len(rest) <= 5


def _split_articles(text: str, folder: str) -> list[dict]:
    lines = text.splitlines()
    law_name = next((l.strip() for l in lines if l.strip()), folder)

    chapter, current, articles = None, None, []
    for line in lines[1:]:               # first non-empty line is the law name
        s = line.strip()
        if not s or s == _AMENDMENT_MARKER:
            continue
        if s.startswith("الباب"):
            chapter = s
            continue
        if s.startswith("الفصل"):        # sub-section heading — context only
            continue
        if _is_article_header(s):
            if current:
                articles.append(current)
            ref = _ARTICLE_HEADER.match(s).group(1).strip()
            current = {"article_ref": ref, "chapter": chapter,
                       "source": law_name, "folder": folder, "lines": []}
            continue
        if current is not None:
            current["lines"].append(s)
    if current:
        articles.append(current)

    out = []
    for a in articles:
        body = "\n".join(a["lines"]).strip()
        if body:
            out.append({"article_ref": a["article_ref"], "text": body,
                        "chapter": a["chapter"], "source": a["source"],
                        "folder": a["folder"]})
    return out


def load_documents() -> list[dict]:
    """Read every corpus subfolder and split each file into article chunks."""
    base = Path(config.DATA_DIR)
    docs: list[dict] = []
    for folder in config.CORPORA:
        folder_dir = base / folder
        if not folder_dir.exists():
            print(f"  (skipping missing corpus: {folder_dir})")
            continue
        n = 0
        for path in sorted(folder_dir.glob("*.txt")):
            parsed = _split_articles(path.read_text(encoding="utf-8"), folder)
            docs.extend(parsed)
            n += len(parsed)
        print(f"  {folder}: {n} articles")
    return docs


def build_index():
    docs = load_documents()
    if not docs:
        print("No articles parsed. Check that the corpus is under", config.DATA_DIR)
        return

    if embeddings.available():
        print(f"Embedding {len(docs)} articles with {config.EMBED_MODEL}...")
        vectors = embeddings.embed([d["text"] for d in docs])
        for d, v in zip(docs, vectors):
            d["embedding"] = v
        mode = "semantic (embeddings)"
    else:
        print("No OpenAI key — writing a text-only index (keyword search at query time).")
        mode = "keyword-only"

    index_path = Path(config.INDEX_PATH)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps({"chunks": docs}, ensure_ascii=False),
                          encoding="utf-8")
    print(f"Indexed {len(docs)} articles -> {index_path}  [{mode}]")


if __name__ == "__main__":
    build_index()
