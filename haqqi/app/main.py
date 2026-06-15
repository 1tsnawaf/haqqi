"""
FastAPI backend. Owned by P3.
Run:  uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from app.schemas import ChatRequest, AgentResponse
from app.agent.loop import run as run_agent

app = FastAPI(title="Haqqi", description="Employment-rights agent (information, not legal advice)")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=AgentResponse)
def chat(req: ChatRequest) -> AgentResponse:
    """Single turn: take the user's message + current case file, return a grounded reply."""
    return run_agent(req)
