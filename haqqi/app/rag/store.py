"""
Vector store. Lightweight by design: a persisted JSON index + in-memory search
via numpy. No external DB to stand up for a hackathon.

Retrieval is HYBRID: semantic (cosine over OpenAI embeddings) combined with an
Arabic-normalised, lightly-stemmed lexical overlap score. The lexical signal
recovers high-confidence matches that `-small` embeddings miss when the user's
plain-language wording differs from the formal statute wording — e.g. a query
about "شركة منافسة" vs Article 83's "ألا يقوم ... بمنافسته". Scores are min-max
normalised and blended, then biased toward the primary corpus (labor_law).
"""
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from app import config
from app.schemas import Citation
from app.rag import embeddings

# --- Arabic normalisation + a light stemmer (dependency-free) --------------------
_DIACRITICS = re.compile(r"[ؗ-ًؚ-ْٰـ]")  # harakat + tatweel
_ALEF = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"})
_WORD = re.compile(r"\w+", re.UNICODE)

# longest-first so the right affix is stripped
_PREFIXES = ("وال", "بال", "كال", "فال", "ال", "لل", "و", "ف", "ب", "ك", "ل")
_SUFFIXES = ("ها", "هم", "هن", "كم", "ات", "ون", "ين", "ان", "ته", "تي", "ني",
             "ه", "ك", "ي", "ا", "ن")


def _normalize(text: str) -> str:
    return _DIACRITICS.sub("", text).translate(_ALEF).lower()


def _stem(tok: str) -> str:
    for p in _PREFIXES:
        if tok.startswith(p) and len(tok) - len(p) >= 3:
            tok = tok[len(p):]
            break
    for s in _SUFFIXES:
        if tok.endswith(s) and len(tok) - len(s) >= 3:
            tok = tok[:-len(s)]
            break
    return tok


def _stems(text: str) -> set[str]:
    return {_stem(t) for t in _WORD.findall(_normalize(text))}


def _minmax(scores: np.ndarray) -> np.ndarray:
    lo, hi = float(scores.min()), float(scores.max())
    if hi - lo < 1e-9:
        return np.zeros_like(scores)
    return (scores - lo) / (hi - lo)


class VectorStore:
    def __init__(self, index_path: str = None):
        self.index_path = Path(index_path or config.INDEX_PATH)
        self._chunks: list[dict] = []
        self._matrix = None
        self._folders: list[str] = []
        self._token_sets: list[set[str]] = []
        self._idf: dict[str, float] = {}
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True
        if not self.index_path.exists():
            return
        data = json.loads(self.index_path.read_text(encoding="utf-8"))
        self._chunks = data.get("chunks", [])
        self._folders = [c.get("folder", "") for c in self._chunks]
        self._token_sets = [_stems(c["text"]) for c in self._chunks]
        # IDF so distinctive terms (e.g. "منافس", df=1) dominate the lexical score
        # over common ones (e.g. "عمل", "عقد").
        n = len(self._chunks)
        df = Counter(t for toks in self._token_sets for t in toks)
        self._idf = {t: math.log(1 + n / c) for t, c in df.items()}
        vecs = [c["embedding"] for c in self._chunks if c.get("embedding")]
        if vecs and len(vecs) == len(self._chunks):
            mat = np.asarray(vecs, dtype=np.float32)
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            self._matrix = mat / np.clip(norms, 1e-8, None)

    @property
    def ready(self) -> bool:
        self._ensure_loaded()
        return bool(self._chunks)

    def query(self, text: str, k: int = 4,
              prefer_folder: str = None, prefer_boost: float = 1.0) -> list[Citation]:
        self._ensure_loaded()
        if not self._chunks:
            return []

        lex = self._lexical_scores(text)
        sem = self._semantic_scores(text)

        if sem is not None:
            combined = (1.0 - config.LEX_WEIGHT) * _minmax(sem) + config.LEX_WEIGHT * _minmax(lex)
        else:
            combined = lex  # no embeddings available -> lexical only

        if prefer_folder and prefer_boost != 1.0:
            boost = np.array([prefer_boost if f == prefer_folder else 1.0
                              for f in self._folders], dtype=np.float32)
            combined = combined * boost

        order = np.argsort(combined)[::-1][:k]
        return [self._to_citation(self._chunks[i]) for i in order if combined[i] > 0]

    def _semantic_scores(self, text: str):
        if self._matrix is None or not embeddings.available():
            return None
        try:
            q = np.asarray(embeddings.embed_one(text), dtype=np.float32)
            q = q / max(np.linalg.norm(q), 1e-8)
            return self._matrix @ q
        except Exception:
            return None

    def _lexical_scores(self, text: str):
        q = _stems(text)
        denom = sum(self._idf.get(t, 0.0) for t in q)
        if denom <= 0:
            return np.zeros(len(self._chunks), dtype=np.float32)
        return np.array(
            [sum(self._idf.get(t, 0.0) for t in (q & toks)) / denom
             for toks in self._token_sets],
            dtype=np.float32,
        )

    @staticmethod
    def _to_citation(chunk: dict) -> Citation:
        return Citation(
            article_ref=chunk["article_ref"],
            text=chunk["text"],
            source=chunk.get("source", "نظام العمل"),
            chapter=chunk.get("chapter"),
            folder=chunk.get("folder"),
        )


# Singleton used by search.py
store = VectorStore()
