# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False) 
    created_at = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    session_title = Column(String(255), nullable=False) 
    # Relationship to chat messages
    messages = relationship("AIChatMessage", back_populates="session", cascade="all, delete-orphan")

class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, nullable=False)
    role = Column(String(10), nullable=False)  # "user" or "ai"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")