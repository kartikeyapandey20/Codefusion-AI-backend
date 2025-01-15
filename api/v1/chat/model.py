from db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship

class UserResponse(Base):
    
    __tablename__ = 'user_response'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response_text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    
class AiResponse(Base):
    
    __tablename__ = 'ai_response'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    response_text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    

class Chat(Base):
    
    __tablename__ = 'chat'
    
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    user_response_id = Column(Integer, ForeignKey("user_response.id", ondelete="CASCADE"), nullable=False)
    ai_response_id = Column(Integer, ForeignKey("ai_response.id", ondelete="CASCADE"), nullable=False)
    
    user_response = relationship("UserResponse")
    ai_response = relationship("AiResponse")