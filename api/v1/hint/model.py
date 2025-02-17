from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from db.database import Base


class AIHintRequest(Base):
    __tablename__ = "ai_hint_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    request_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    hint_response = Column(Text, nullable=False)