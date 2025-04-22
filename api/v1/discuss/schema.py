from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class DiscussionMessageBase(BaseModel):
    content: str = Field(..., min_length=1)

class DiscussionMessageCreate(DiscussionMessageBase):
    thread_id: int
    user_id: int

class DiscussionMessageOut(DiscussionMessageBase):
    id: int
    thread_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class DiscussionThreadBase(BaseModel):
    question_id: int
    user_id: int
    title: str = Field(..., max_length=255)

class DiscussionThreadCreate(DiscussionThreadBase):
    pass

class DiscussionThreadOut(DiscussionThreadBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class StartDiscussionRequest(BaseModel):
    question_id: int
    user_id: int
    title: str = Field(..., max_length=255)
    content: str = Field(..., min_length=1)

class NewDiscussionResponse(BaseModel):
    thread: DiscussionThreadOut
    message: DiscussionMessageOut
