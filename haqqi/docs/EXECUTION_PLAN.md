# Haqqi — 2-Day Execution Plan (3-person team)

Companion to the Haqqi PRD. Built for a 3-person team, so it optimizes for two things above all:

1. **Integrate end-to-end on Day 1** — a thin, working pipeline beats three perfect-but-disconnected parts.
2. **Protect one golden-path demo** — build only what that demo needs; everything else is roadmap.

---

## Roles (3 people)

Each person owns one vertical slice and is the decision-maker for it. You'll help each other, but ownership avoids two people editing the same file at 2am.

| Person | Owns | Best fit |
|---|---|---|
| **P1 — Agent / LLM lead** | The agent loop, prompting, tool definitions, and the three behaviors (X-ray, Rights radar, Battle plan logic). The "brain." | Agentic AI / strong prompting |
| **P2 — RAG / Data lead** | Curate the Labor Law knowledge base, chunk + embed, vector store, the `search_law` tool, citation plumbing. The "grounding." | AI/ML + Python |
| **P3 — Backend + UI + Demo lead** | FastAPI orchestration glue, Streamlit chat UI + live case-file card, Docker, **and owns the slides + demo rehearsal.** | SDE Python |

> With only 3 people, the "product/presentation" role a 4th person would hold gets folded into P3. That's deliberate — someone must own the demo from hour one, not the last hour.

---

## Pre-hackathon prep (do this BEFORE the event)

This is where a 3-person team wins or loses. The doc encourages it; for you it's mandatory.

- [ ] **All:** clone the FastAPI, RAG, Agent, and Docker starter templates; confirm they run locally.
- [ ] **All:** get LLM API keys working (OpenAI / Anthropic / Gemini) — test a "hello world" call each.
- [ ] **P2:** obtain the **actual Saudi Labor Law text** in a clean, copy-able format. This is your source of truth — do not paraphrase from memory.
- [ ] **All:** agree the **interfaces** (the contracts between slices) so you can work in parallel:
  - `search_law(query) -> [{text, article_ref, source}]`
  - `agent.run(message, profile) -> {reply, updated_profile, citations}`
  - UI ↔ backend request/response shape
- [ ] **P1:** draft first-pass system prompt for the agent's persona ("employment-rights advocate; information not advice; always cite").

If the interfaces are agreed up front, the three of you can build in parallel without blocking each other.

---

## Day 1 — Skeleton, then flesh

**Goal of Day 1:** a user can type one employment question and get a cited answer, end-to-end, in the real UI. Ugly is fine. Connected is the point.

### Block 1 — Kickoff & setup (~first 1–1.5 hrs)
- Team formation activity + finalize problem statement → **fast**, you already have the PRD.
- Stand up the shared repo, branch strategy, and the agreed interfaces.
- Confirm everyone can run the skeleton locally.

### Block 2 — Parallel build of the three slices (rest of morning → early afternoon)
- **P2:** ingest Labor Law → chunk → embed → vector store. `search_law` returns relevant articles **with citation refs**.
- **P1:** agent loop scaffold with LLM tool-calling. Minimal flow: understand → call `search_law` → answer with a citation. No fancy behaviors yet.
- **P3:** FastAPI endpoint + Streamlit chat UI + a **case-file card stub** (even hardcoded) + Dockerfile.

### Block 3 — FIRST INTEGRATION (mid-afternoon) ⚠️ most important block of the event
- Wire it together: **UI → FastAPI → agent → `search_law` → cited answer → back to UI.**
- Don't move on until a real question produces a real cited answer through the real stack.

### ✅ Day 1 exit checkpoint
> Type *"Can my employer withhold my salary?"* → get a plain-language answer **with a cited article**, displayed in the UI, with the case-file card showing.

If you hit this, you are in great shape. If not, **all three** stop and fix integration before Day 2.

---

## Day 2 — Behaviors, then polish & demo

**Goal of Day 2:** the three signature behaviors work on **one scripted scenario**, and the demo + slides are rehearsed.

### Block 4 — Layer the three behaviors (morning)
- **P1:** add
  - **Rights radar** — prompt the agent to proactively surface entitlements not asked about.
  - **Contract X-ray** — accept pasted contract text; flag problematic clauses with article citations.
  - **Battle plan** — `draft_action` tool that outputs a letter / script / evidence checklist.
- **P2:** tune retrieval quality for the demo scenario; verify citation accuracy; load enough KB coverage for the chosen scenario; wire bilingual handling.
- **P3:** make the case-file card **update live**; polish UI; add the legal disclaimer + "verify with a professional" flag; bilingual UI labels.

### Block 5 — Build & harden the GOLDEN PATH (midday) → then FEATURE FREEZE
- Lock the exact demo scenario (see PRD §9 — the "fired after 3 years + non-compete" story works well).
- Run it end-to-end until it works **flawlessly**, every time.
- **Record a backup screen capture** in case live fails.
- 🧊 **Feature freeze after this block.** No new features. Only bug-fixing and polish from here.

### Block 6 — Slides + rehearsal + buffer (afternoon)
- **P3 leads slides** (all contribute content); map straight from the PRD:
  1. Problem Statement → PRD §2
  2. Motivation → PRD §2–3
  3. Solution & Architecture → PRD §6–8
  4. Live Demo → the golden path
  5. Future Roadmap → PRD §10 (the what-if simulator headlines this)
- Rehearse the demo **2–3 times**, assign who says what.
- Keep the last block as pure **buffer** — something always breaks.

### Final — Present.

---

## If you fall behind: graceful-degradation cut order

Cut from the bottom up. Each line down still leaves a coherent, demoable product.

1. *(Stretch)* What-if simulator — drop first, it's already roadmap.
2. Bilingual support — English-only is fine for the demo.
3. Battle plan → reduce to a single drafted letter (skip script + evidence list).
4. Contract X-ray → reduce to flagging **one** known clause in a prepared sample contract.
5. Rights radar → keep (it's cheap and high-impact).
6. **Never cut:** cited end-to-end answers + the live case-file card. That alone is a credible agent demo.

---

## The three failure modes to actively avoid

- **Big-bang integration.** Wiring everything together at the end is the #1 hackathon killer. You integrate in Day 1 Block 3, on purpose.
- **Building off the demo path.** Every hour spent on a feature that isn't in the golden path is an hour stolen from making the demo flawless.
- **Slides as an afterthought.** P3 owns them from the start; they're built *from* the PRD, not from scratch at hour 47.

---

*North star: one real employment situation → rights found with citations → a flagged clause → an actionable next step. If that works on stage, you've hit the success definition.*
