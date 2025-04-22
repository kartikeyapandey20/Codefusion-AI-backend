from db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime

class DiscussionThread(Base):
    __tablename__ = "discussion_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to discussion messages
    messages = relationship("DiscussionMessage", back_populates="thread", cascade="all, delete-orphan")

class DiscussionMessage(Base):
    __tablename__ = "discussion_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("discussion_threads.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to thread
    thread = relationship("DiscussionThread", back_populates="messages")