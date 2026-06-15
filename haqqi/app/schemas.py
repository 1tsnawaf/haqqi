"""
Shared data contracts for Haqqi.

These models are the *interfaces* between the three slices (agent / rag / ui).
Agree on these first; then P1, P2, P3 can build in parallel without blocking.
"""
from typing import Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A grounded reference to the source law. Every conclusion must carry one."""
    article_ref: str                       # e.g. "Article 77"
    text: str                              # the relevant passage (paraphrase or short quote)
    source: str = "Saudi Labor Law"


class Profile(BaseModel):
    """The agent's running understanding of the user — i.e. the live 'case file'."""
    role: Optional[str] = None
    tenure_years: Optional[float] = None
    monthly_salary: Optional[float] = None
    employment_status: Optional[str] = None     # employed | terminated | resigned | seeking
    issue: Optional[str] = None                 # short description of the problem
    extra: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str
    profile: Profile = Field(default_factory=Profile)
    language: str = "en"                        # "en" or "ar"


class FlaggedClause(BaseModel):
    """Output of Contract X-ray."""
    clause: str
    issue: str
    citation: Citation


class AgentResponse(BaseModel):
    reply: str
    profile: Profile                            # updated case file (so UI can re-render it)
    citations: list[Citation] = Field(default_factory=list)
    flagged_clauses: list[FlaggedClause] = Field(default_factory=list)
    needs_user_input: bool = False              # True when the agent asked a clarifying question
