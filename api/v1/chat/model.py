from db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey,Text , CheckConstraint
from sqlalchemy.orm import relationship

class AIChatMessage(Base):
    
    __tablename__ = 'ai_chat_messages'
    
    id = Column(Integer, primary_key=True, nullable=False)
    session_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(10),nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'ai')", name="chk_role_valid"),
    )