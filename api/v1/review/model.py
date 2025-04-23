# models.py
from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func, String, Boolean, JSON
from sqlalchemy.orm import relationship
from db.base import Base

class AIReview(Base):
    __tablename__ = "ai_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    review_text = Column(Text, nullable=False)
    code_quality_score = Column(Integer, nullable=True)  # Score from 1-10
    compliance_status = Column(Boolean, nullable=True)  # True if code passes compliance checks
    test_results = Column(JSON, nullable=True)  # JSON containing test case results
    suggestions = Column(Text, nullable=True)  # Improvement suggestions
    security_issues = Column(Text, nullable=True)  # Identified security issues
    performance_notes = Column(Text, nullable=True)  # Performance-related feedback
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationship to the submission
    submission = relationship("Submission", back_populates="ai_reviews")
