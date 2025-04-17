from typing import List, Optional
from pydantic import BaseModel, Field

class QuestionExample(BaseModel):
    id: int 
    input: dict
    output: int

class QuestionTestCase(BaseModel):
    id: int 
    input: dict
    exp_output: int
class QuestionConstraint(BaseModel):
    id: int
    question_id: int
    description: str
class QuestionBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    examples: List[QuestionExample]
    constraints: List[QuestionConstraint]
    test_cases: List[QuestionTestCase]

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    difficulty_level: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    examples: Optional[List[QuestionExample]] = None
    constraints: Optional[List[QuestionConstraint]] = None
    test_cases: Optional[List[QuestionTestCase]] = None

class QuestionResponse(QuestionBase):
    id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class QuestionsListResponse(BaseModel):
    total: int
    questions: List[QuestionResponse]
