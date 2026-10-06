from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScoreBreakdown(BaseModel):
    ai_project_depth: int = Field(default=0, description="Score 0-40")
    python_backend: int = Field(default=0, description="Score 0-30")
    cloud_fullstack: int = Field(default=0, description="Score 0-15")
    github: int = Field(default=0, description="Score 0-10")
    engineering_depth: int = Field(default=0, description="Score 0-5")

class LLMEvaluation(BaseModel):
    score_breakdown: ScoreBreakdown
    matched_skills: List[str]
    project_summary: str
    strengths: List[str]
    concerns: List[str]

class CandidateResult(BaseModel):
    rank: int = 0
    candidate_name: str
    eligible: bool
    total_score: int = 0
    score_breakdown: Optional[ScoreBreakdown] = None
    matched_skills: List[str] = []
    project_summary: Optional[str] = None
    github_summary: Optional[str] = None
    strengths: List[str] = []
    concerns: List[str] = []
    rejection_reasons: List[str] = []
    
    # Internal fields not dumped to final JSON if not needed, or kept for tracking
    file_path: Optional[str] = None
    github_url: Optional[str] = None

class BatchSummary(BaseModel):
    total_resumes: int
    successfully_parsed: int
    eligible: int
    rejected: int
    failed: int
