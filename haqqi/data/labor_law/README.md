# Knowledge base — the Arabic legal corpus

Haqqi is grounded in two corpora, one subfolder each under `data/`:

| Folder | Role | Law | ~Articles |
|---|---|---|---|
| `labor_law/` | **Primary** — employment questions | نظام العمل | ~227 |
| `civil_procedure/` | Secondary — "where/how to file" | نظام المرافعات الشرعية | ~184 |

Retrieval biases toward `labor_law` (see `PRIMARY_BOOST` in `app/config.py`), so
employment questions stay grounded in the labor law while civil-procedure articles
still surface for filing questions.

## File format (UTF-8)

- Line 1 is the law name (e.g. `نظام العمل`).
- Chapter headings start with `الباب`; section headings start with `الفصل`.
- Articles are delimited by header lines like `المادة الخامسة والخمسون :` (the number
  is in Arabic words). The body runs until the next such header.
- Lines equal to `تعديلات المادة` (amendment markers) are ignored.

## Build / rebuild the index

```bash
python -m app.rag.ingest
```

This parses one chunk per article (keeping `article_ref`, `chapter`, `source` law
name, and `folder`), embeds each with `text-embedding-3-small`, and writes
`data/.index.json`. Re-run after any change to the corpus. Without an `OPENAI_API_KEY`
it writes a text-only index and retrieval falls back to (Arabic-aware) keyword search.
