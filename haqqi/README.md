# Haqqi (حقّي) — know your employment rights

> An AI **agent** that helps regular people understand and act on their employment rights.
> It works your case like an advocate: investigates your situation (or your contract),
> flags what you missed — including clauses that are actually unenforceable — and hands
> you a plan to act.
>
> **This is legal _information_, not legal advice.** Consult a licensed lawyer for your case.

Built for the WeCloudData "From Coding to Intelligence" Hackathon · SDA May Cohort 2026.

---

## What it does (3 behaviors)

1. **Contract X-ray** — audits a contract clause-by-clause, flagging unlawful/unenforceable terms with a cited article.
2. **Rights radar** — proactively surfaces entitlements you didn't think to ask about.
3. **Battle plan** — drafts the letter / script / evidence checklist and tells you where to file.

Grounded in the Saudi Labor Law via RAG, with a source citation on every conclusion and a live "case-file" card so you can see what the agent understands.

## Quickstart

> ⚠️ Use a fresh virtualenv. A globally-installed old FastAPI/Pydantic mix will fail
> to import — the pinned versions in `requirements.txt` are what's tested.

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then add your OPENAI_API_KEY

# build the knowledge base index from the Arabic corpus in data/
python -m app.rag.ingest

# terminal 1 — backend
uvicorn app.main:app --reload

# terminal 2 — UI
streamlit run ui/streamlit_app.py
```

With `OPENAI_API_KEY` set you get real, grounded answers. With **no key**, the app
still runs end-to-end in MOCK mode (deterministic reply + keyword retrieval), so the
pipeline never hard-blocks.

## Status — the logic is wired

The three behaviors, RAG, and the agent loop are implemented (OpenAI-backed):

| Piece | State | File(s) |
|---|---|---|
| Arabic corpus + index (~411 articles: labor_law + civil_procedure, semantic + keyword) | ✅ | `data/`, `app/rag/*` |
| LLM provider (OpenAI gpt-4o; text + JSON modes; mock fallback) | ✅ | `app/agent/llm.py`, `.env` |
| 3 behaviors (X-ray, Rights radar, Battle plan) | ✅ | `app/behaviors/*.py` |
| Agent loop (understand → retrieve → radar → ask → deliver + plan) | ✅ | `app/agent/loop.py` |
| UI: Arabic / RTL, live case file, flagged clauses, cited article refs | ✅ | `ui/streamlit_app.py` |

The agent answers **in Arabic**, grounded strictly in the retrieved articles, citing
the governing article (e.g. `المادة الرابعة والثمانون`) on every legal point. See
`data/labor_law/README.md` for the corpus format and how retrieval biases toward the
labor law.

## Project structure

```
haqqi/
├── app/
│   ├── schemas.py        # shared data contracts (agree these first)
│   ├── config.py         # settings / env
│   ├── main.py           # FastAPI backend  (P3)
│   ├── agent/            # the agent brain  (P1)
│   │   ├── loop.py        #   bounded loop: understand→retrieve→evaluate→ask→deliver
│   │   ├── tools.py       #   search_law · ask_user · draft_action
│   │   ├── prompts.py     #   persona / system prompt
│   │   └── llm.py         #   LLM wrapper (mock by default)
│   ├── rag/              # grounding         (P2)
│   │   ├── ingest.py · store.py · search.py
│   └── behaviors/       # the 3 behaviors    (P1)
│       ├── xray.py · rights_radar.py · battle_plan.py
├── ui/streamlit_app.py   # chat UI + case-file card (P3)
├── data/labor_law/       # put the verified law text here
├── docs/                 # PRD.md + EXECUTION_PLAN.md
├── Dockerfile · docker-compose.yml · requirements.txt · .env.example
```

See `docs/PRD.md` for the full product spec and `docs/EXECUTION_PLAN.md` for the 2-day plan.

## Disclaimer

Haqqi provides general legal information based on publicly available law. It is not a
lawyer, does not provide legal advice, and does not create a lawyer–client relationship.
Always verify with a licensed professional.
