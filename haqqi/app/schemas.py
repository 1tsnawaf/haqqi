"""
Shared data contracts for Haqqi.

These models are the *interfaces* between the three slices (agent / rag / ui).
Agree on these first; then P1, P2, P3 can build in parallel without blocking.
"""
from typing import Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    """A grounded reference to the source law. Every conclusion must carry one."""
    article_ref: str                       # e.g. "المادة الرابعة والثمانون"
    text: str                              # the article body
    source: str = "نظام العمل"             # the law name (file's first line)
    chapter: Optional[str] = None          # the الباب heading the article sits under
    folder: Optional[str] = None           # "labor_law" | "civil_procedure"


class Profile(BaseModel):
    """The agent's running understanding of the user — i.e. the live 'case file'."""
    role: Optional[str] = None
    tenure_years: Optional[float] = None
    monthly_salary: Optional[float] = None
    employment_status: Optional[str] = None     # employed | terminated | resigned | seeking
    issue: Optional[str] = None                 # short description of the problem
    # Facts a termination/resignation conclusion depends on — gathered before the
    # agent computes compensation, notice pay, or for-cause outcomes.
    contract_type: Optional[str] = None         # "fixed-term" | "indefinite"
    notice_given: Optional[str] = None          # e.g. "none" | "30 days" | "yes"
    termination_reason: Optional[str] = None    # stated reason / "for cause" vs not
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
