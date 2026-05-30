from pydantic import BaseModel
from typing import Optional


class ContractAnalysisRequest(BaseModel):
    instructions: str = ""
    voice_note_text: str = ""


class ClauseHighlight(BaseModel):
    clause: str
    risk_level: str
    explanation: str


class RecommendedRevision(BaseModel):
    clause: str
    current_text: str
    suggested_revision: str
    reason: str


class ContractAnalysisResponse(BaseModel):
    filename: str
    risk_summary: str
    risk_score: int
    highlighted_clauses: list[ClauseHighlight]
    recommended_revisions: list[RecommendedRevision]


class ErrorResponse(BaseModel):
    detail: str
