from datetime import datetime
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP, func, String , DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from db.base import Base


# Primary Question model.
class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty_level = Column(String(50), nullable=False)  # e.g., Easy, Medium, Hard
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships to associated tables.
    examples = relationship("QuestionExample", back_populates="question", cascade="all, delete-orphan")
    constraints = relationship("QuestionConstraint", back_populates="question", cascade="all, delete-orphan")
    test_cases = relationship("QuestionTestCase", back_populates="question", cascade="all, delete-orphan")


# Model to store examples for a question.
class QuestionExample(Base):
    __tablename__ = "question_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    input = Column(JSONB, nullable=False)    # e.g., {"source": "listen", "target": "silent"}
    output = Column(Integer, nullable=False)  # e.g., 0
    
    question = relationship("Question", back_populates="examples")


# Model to store constraints for a question.
class QuestionConstraint(Base):
    __tablename__ = "question_constraints"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    
    question = relationship("Question", back_populates="constraints")


# Model to store test cases for a question.
class QuestionTestCase(Base):
    __tablename__ = "question_test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    input = Column(JSONB, nullable=False)      # e.g., {"source": "test", "target": "sett"}
    exp_output = Column(Integer, nullable=False) # expected output
    
    question = relationship("Question", back_populates="test_cases")
