from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func, String
from sqlalchemy.orm import relationship
from db.base import Base

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    result = Column(String(50), nullable=True)  # e.g., "Accepted", "Wrong Answer", etc.
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())