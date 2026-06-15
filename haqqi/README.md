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

## Quickstart (runs in MOCK mode, no API key needed)

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# terminal 1 — backend
uvicorn app.main:app --reload

# terminal 2 — UI
streamlit run ui/streamlit_app.py
```

Open the Streamlit URL, type a question, and you'll get a (mock) cited answer end-to-end.
That's the **walking skeleton** — now fill in the real logic.

## Make it real

| Step | Owner | File(s) |
|---|---|---|
| Add the verified Labor Law text + build the index | P2 | `data/labor_law/`, `app/rag/ingest.py`, `app/rag/store.py`, `app/rag/search.py` |
| Wire a real LLM provider | P1 | `app/agent/llm.py`, `.env` |
| Implement the 3 behaviors | P1 | `app/behaviors/*.py`, `app/agent/loop.py` |
| Polish UI + case-file card + disclaimer | P3 | `ui/streamlit_app.py`, `app/main.py` |

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
