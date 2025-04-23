from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TestResult(BaseModel):
    test_name: str
    passed: bool
    message: Optional[str] = None
    execution_time: Optional[float] = None


class AIReviewBase(BaseModel):
    submission_id: int
    review_text: str
    code_quality_score: Optional[int] = Field(None, ge=1, le=10)  # Score from 1-10
    compliance_status: Optional[bool] = None
    suggestions: Optional[str] = None
    security_issues: Optional[str] = None
    performance_notes: Optional[str] = None


class AIReviewCreate(AIReviewBase):
    test_results: Optional[List[TestResult]] = None


class AIReviewUpdate(BaseModel):
    review_text: Optional[str] = None
    code_quality_score: Optional[int] = Field(None, ge=1, le=10)
    compliance_status: Optional[bool] = None
    test_results: Optional[List[TestResult]] = None
    suggestions: Optional[str] = None
    security_issues: Optional[str] = None
    performance_notes: Optional[str] = None


class AIReviewOut(AIReviewBase):
    id: int
    created_at: datetime
    test_results: Optional[List[TestResult]] = None

    class Config:
        orm_mode = True


# For backward compatibility
class AIReviewResponse(AIReviewOut):
    pass


class AIReviewInDB(AIReviewOut):
    pass
