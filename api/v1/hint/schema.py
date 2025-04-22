from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class HintRequestBase(BaseModel):
    question_id: int
    user_id: int

class HintRequest(HintRequestBase):
    pass

class HintResponse(BaseModel):
    hint: str
    request_id: int
    question_id: int
    user_id: int
    request_time: datetime
    
    model_config = ConfigDict(from_attributes=True)

class HintHistoryItem(BaseModel):
    id: int
    question_id: int
    user_id: int
    request_time: datetime
    hint: str
    
    model_config = ConfigDict(from_attributes=True)