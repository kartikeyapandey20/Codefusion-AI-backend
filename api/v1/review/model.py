from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func, String
from sqlalchemy.orm import relationship
from db.base import Base

class AIReview(Base):
    __tablename__ = "ai_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    review_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
