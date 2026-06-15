# Haqqi (حقّي) — Product Requirements Document

**An AI agent that helps regular people understand and act on their employment rights.**

*Prepared for: WeCloudData "From Coding to Intelligence" Hackathon — SDA May Cohort 2026*
*Domain: Government & Public Services · Track focus: Agentic AI + SDE Python*

---

## 1. One-line pitch

Haqqi works your case like an employment-rights advocate: you describe your situation (or paste your contract), and the agent investigates it, flags what you missed — including clauses that are actually unenforceable — and hands you a plan to act. It is legal **information**, not legal advice.

---

## 2. Problem statement

Most employees do not know their rights at work, and the people most likely to be treated unfairly are the least likely to be able to afford a lawyer to find out. The law that protects them exists and is publicly available, but it is written in dense legal language, scattered across articles, and almost no one reads it until something has already gone wrong — an unpaid wage, a sudden termination, a contract they signed without understanding.

The result is a large, everyday gap: people forfeit money and protections they are legally entitled to, simply because they never knew the right question to ask.

---

## 3. Target user

Regular employees and job-seekers — not lawyers, not legal professionals. People who:

- have just been fired, had wages withheld, or are in a dispute with an employer
- are about to sign an employment contract and want to know if it is fair
- want to understand a specific right (end-of-service pay, notice period, leave) before acting

The product assumes **no legal knowledge** and speaks in plain language (Arabic and English).

---

## 4. Goals and non-goals

**Goals**
- Let a user understand their employment rights from a plain-language description of their situation.
- Ground every answer in the actual law, with a citation to the source article.
- Move the user from "confused" to "I know what I'm owed and what to do next."
- Demonstrate genuine **agentic** behavior — reasoning, tool use, and proactive investigation — not a Q&A chatbot.

**Non-goals (explicitly out of scope for the MVP)**
- Not a lawyer and not legal advice — it informs and points to professionals; it does not represent anyone.
- Not a general legal assistant — employment law only.
- Not a research tool for lawyers.
- No live integration with government or court systems.
- No production-grade accuracy guarantees, polished UI, or large-scale deployment (per hackathon rules).

---

## 5. Why an agent, not a chatbot

This is the core technical bet, and it maps directly to the "AI Utilization" judging criterion.

A chatbot **responds** to the question asked. An agent **works toward a goal** — here, "find out what this person is entitled to and help them act." Haqqi runs a reasoning loop, decides what information it still needs, calls tools to retrieve and reason over the law, and proactively surfaces things the user never asked about. That autonomy and tool use is what makes it an agent, and it is exactly what an employment-rights problem requires, because the issue is rarely a single fact — it is a messy situation that has to be matched against multiple rules and turned into a decision and an action.

---

## 6. Core features (the locked behavior set)

The agent's personality is built from three behaviors that compose into one flow: **investigate → discover → arm.**

### 6.1 Contract X-ray — the signature feature
The user pastes or uploads their employment contract (or describes their situation), and the agent audits it clause by clause, flagging any term that **violates the user's rights or is unenforceable**, with a citation to the governing article.

> Example: *"Clause 6 says you forfeit your end-of-service pay if you resign — under the Labor Law, that protection generally cannot be waived. Here's the relevant article."*

This is the standout demo moment — the "wait, that's actually illegal?" beat.

### 6.2 Rights radar — proactive discovery
Rather than only answering what was asked, the agent investigates the situation and surfaces entitlements the user did not know to mention — unpaid overtime, unused-leave payout, notice rights, end-of-service eligibility. This is the "rights you're leaving on the table" behavior that makes Haqqi an advocate rather than a search box.

### 6.3 Battle plan — turn knowledge into action
Once the agent understands the situation, it produces the concrete next step:
- a drafted letter or complaint the user can send,
- a short script of what to say to HR or the employer,
- a checklist of evidence to gather,
- and where to take the issue (the relevant labor office / channel).

### Supporting features (build alongside the core)
- **Source citations** — every conclusion links to the exact article it came from. Builds trust and visibly separates Haqqi from a chatbot. (Nearly free — the retrieval already returns the source.)
- **Live "case file" card** — an on-screen panel showing what the agent currently understands (role, tenure, salary, issue), updating as the conversation goes. This is the best way to *show* it is an agent with memory and state.
- **Bilingual Arabic ⇄ English** — handled natively by the LLM; a major accessibility and impact win.
- **Safety layer** — clear "this is legal information, not legal advice; consult a licensed lawyer for your specific case" framing, plus a "verify with a professional" flag when the agent is uncertain.

---

## 7. How it works — agent loop and tools

The agent runs a bounded loop:

1. **Understand** — parse the user's situation (and/or contract) into a structured profile.
2. **Retrieve** — search the employment-law knowledge base for the relevant articles (RAG).
3. **Evaluate** — reason over the retrieved rules: which rights apply, which clauses are problematic, what is the user owed.
4. **Ask** — if a decision needs missing information (salary, tenure, reason for leaving), ask the user, then loop back. Capped at ~3 clarifying questions so it never wanders.
5. **Deliver** — present rights found (with citations), flagged clauses, and the battle plan.

**Tools the agent can call**
- `search_law(query)` — RAG over the curated Labor Law knowledge base; returns relevant articles with sources.
- `ask_user(question)` — requests a missing fact, then resumes.
- `draft_action(profile, issue)` — generates the letter / script / evidence checklist.

Three tools plus an LLM reasoning loop is a real agent. Resist adding more during the build.

---

## 8. Technical architecture

Maps directly onto four of the five suggested hackathon starter templates:

| Layer | Choice | Maps to |
|---|---|---|
| Chat UI + case-file card | Streamlit or the chatbot starter | AI Chatbot Starter Template |
| Backend / orchestration | FastAPI | FastAPI Starter Template |
| Knowledge retrieval | RAG over curated Labor Law text | RAG Pipeline Template |
| Agent loop + tool calling | Agent framework or native tool use | Agent Framework Template |
| Packaging for demo | Docker | Docker Deployment Template |
| Reasoning | Hosted LLM API (OpenAI / Anthropic / Gemini) | No model training required |

**Knowledge base:** curate the relevant sections of the current Saudi Labor Law into clean, chunked source documents. The exact article text must be loaded from the verified law — not written from memory — because citation accuracy is the product's credibility.

---

## 9. Primary user flow (also the live demo script)

> **User:** "My company fired me last week after 3 years. They say I get no end-of-service pay because it was 'for performance.' My contract also bans me from working for a competitor for 2 years."
>
> **Haqqi:** asks two clarifying questions — *Was there a prior written warning? What was your monthly salary?* (Case-file card fills in: 3 yrs tenure, terminated, salary entered.)
>
> **Rights radar:** surfaces that termination still generally entitles the user to end-of-service pay unless specific for-cause conditions are met, plus unused-leave payout and notice rights the user never asked about — each with a cited article.
>
> **Contract X-ray:** flags the 2-year non-compete as likely unenforceable as written, citing the governing article.
>
> **Battle plan:** drafts a letter to the employer / labor office, lists the documents to gather as evidence, and explains where to file.

That single flow demonstrates reasoning, tool use, RAG grounding, proactive discovery, and real value — most of the scorecard in about 90 seconds.

---

## 10. Scope: MVP vs roadmap (Slide 5)

**In the MVP**
- The three core behaviors (X-ray, Rights radar, Battle plan)
- Employment law only, one jurisdiction (Saudi)
- Citations, live case-file card, bilingual, safety layer
- One polished end-to-end demo scenario

**Roadmap (deliberately deferred — this is your Future Vision slide)**
- **What-if simulator** — compare outcomes (e.g., resign vs. be terminated). *Qualitative version is cheap and can be a stretch goal; numeric version (actual SAR amounts via a deterministic end-of-service calculator tool) is a strong but optional add.*
- Other areas of law (tenancy, consumer, business)
- Full document drafting suite
- Photo/scan understanding of letters and forms (vision)
- Appeal / rejection helper
- Household / multi-party view

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| **Crossing into "legal advice" / unauthorized practice** | Frame strictly as legal *information*; prominent disclaimer; always point to a licensed professional for the specific case. |
| **Inaccurate legal citations (hallucination)** | Ground every claim in retrieved source text; load the verified law, not memory; show the cited article so it is auditable. |
| **Scope creep** | Behavior set is locked at three; everything else is roadmap. "Solve one problem well." |
| **Agent wanders / loops forever** | Bounded loop, ≤3 clarifying questions, clear stop condition. |
| **Demo fails live** | Rehearse one scripted golden-path scenario; have a recorded fallback. |

---

## 12. Success metrics (aligned to judging criteria)

| Judging criterion | Weight | How Haqqi scores |
|---|---|---|
| Problem Relevance & Impact | 20% | Universal, high-stakes everyday problem; clear unmet need. |
| AI Utilization | 20% | Genuine agent: reasoning loop, tool use, proactive investigation. |
| Technical Implementation | 20% | RAG + agent orchestration + citations + case-file state. |
| Creativity & Innovation | 15% | The "that clause is illegal" X-ray beat; advocate behavior, not Q&A. |
| Demo Quality | 15% | One tight, surprising, relatable scenario end-to-end. |
| Future Vision & Scalability | 10% | Concrete roadmap (what-if, more legal areas, vision input). |

**Definition of success:** a working MVP that takes one real employment situation, finds the user's rights with citations, flags a problematic clause, and produces an actionable next step — clearly framed as information, not advice.

---

*Reminder for the team: load the actual Labor Law text into the knowledge base and verify all article references before the demo. Citation accuracy is the credibility of the entire product.*
