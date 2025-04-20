from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AIChatMessageBase(BaseModel):
    message: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(user|ai)$")

class AIChatMessageCreate(AIChatMessageBase):
    session_id: Optional[int] = None
    user_id: int

class AIChatMessageOut(AIChatMessageBase):
    id: int
    session_id: int
    user_id: int
    created_at: datetime
    session_title: str 
    class Config:
        orm_mode = True
class ChatMessageOut(AIChatMessageBase):
    id: int
    session_id: int
    user_id: int
    created_at: datetime
    class Config:
        orm_mode = True

# 👇 UPDATED with session_title
class ChatSessionBase(BaseModel):
    user_id: int
    session_title: str = Field(..., max_length=255)

class ChatSessionCreate(ChatSessionBase):
    pass

# 👇 UPDATED with session_title
class ChatSessionOut(ChatSessionBase):
    id: int
    created_at: datetime
    last_active: datetime

    class Config:
        orm_mode = True

class StartChatRequest(BaseModel):
    user_id: int
    message: str = Field(..., min_length=1)

class NewChatResponse(BaseModel):
    session_id: int
    message: AIChatMessageOut
