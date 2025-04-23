from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from api.v1.review.schema import AIReviewOut


class SubmissionBase(BaseModel):
    user_id: int
    question_id: int
    code: str = Field(..., min_length=1)
    language: Optional[str] = Field(None, max_length=50)


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1)
    language: Optional[str] = Field(None, max_length=50)
    result: Optional[str] = None
    test_cases_passed: Optional[int] = Field(None, ge=0)
    total_test_cases: Optional[int] = Field(None, ge=0)
    compliance_check: Optional[bool] = None


class SubmissionOut(SubmissionBase):
    id: int
    result: Optional[str] = None
    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None
    compliance_check: Optional[bool] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


# For backward compatibility
class SubmissionResponse(SubmissionOut):
    pass


class SubmissionInDB(SubmissionOut):
    pass


class SubmissionWithReviews(SubmissionOut):
    ai_reviews: List[AIReviewOut] = []


class CodeSubmitRequest(BaseModel):
    user_id: int
    question_id: int
    code: str = Field(..., min_length=1)
    language: str = Field(..., max_length=50)


class SubmitAndReviewResponse(BaseModel):
    submission_id: int
    review: Optional[AIReviewOut] = None
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True