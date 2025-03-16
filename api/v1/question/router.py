from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from .domain import QuestionDomain
from .model import Question
from core.deps import get_db
from .schema import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionsListResponse
)

class QuestionRouter:
    def __init__(self) -> None:
        self.tags = ["Questions"]
        
    @property
    def router(self):
        """
        Get the API router for questions.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(
            prefix="/questions",
            tags=self.tags,
            responses={
                404: {"description": "Not found"},
                400: {"description": "Bad request"},
                500: {"description": "Internal server error"}
            }
        )
        
        @api_router.post("/", response_model=QuestionResponse, status_code=201)
        async def create_question(
            question: QuestionCreate,
            db: Session = Depends(get_db)
        ):
            """
            Create a new question with examples, constraints, and test cases.
            """
            try:
                domain = QuestionDomain(db)
                question_obj = domain.create_question(
                    title=question.title,
                    description=question.description,
                    difficulty_level=question.difficulty_level,
                    examples=[example.dict() for example in question.examples],
                    constraints=[str(constraint) for constraint in question.constraints],  # Convert constraints to strings
                    test_cases=[test_case.dict() for test_case in question.test_cases]
                )
                
                # Convert datetime fields to string
                question_obj.created_at = question_obj.created_at.isoformat() if isinstance(question_obj.created_at, datetime) else question_obj.created_at
                question_obj.updated_at = question_obj.updated_at.isoformat() if isinstance(question_obj.updated_at, datetime) else question_obj.updated_at

                return question_obj
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

        @api_router.get("/{question_id}", response_model=QuestionResponse)
        async def get_question(
            question_id: int,
            db: Session = Depends(get_db)
        ):
            """
            Get a specific question by ID.
            """
            try:
                domain = QuestionDomain(db)
                question = domain.get_question(question_id)
                if not question:
                    raise HTTPException(status_code=404, detail="Question not found")
                
                # Convert datetime fields to string
                question.created_at = question.created_at.isoformat() if isinstance(question.created_at, datetime) else question.created_at
                question.updated_at = question.updated_at.isoformat() if isinstance(question.updated_at, datetime) else question.updated_at
                
                return question
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

        @api_router.get("/", response_model=QuestionsListResponse)
        async def get_questions(
            skip: int = Query(0, ge=0, description="Number of questions to skip"),
            limit: int = Query(10, ge=1, le=1000, description="Maximum number of questions to return"),
            db: Session = Depends(get_db)
        ):
            """
            Get a list of questions with pagination.
            """
            try:
                domain = QuestionDomain(db)
                questions = domain.get_questions(skip=skip, limit=limit)
                
                # Convert datetime fields to string
                for question in questions:
                    question.created_at = question.created_at.isoformat() if isinstance(question.created_at, datetime) else question.created_at
                    question.updated_at = question.updated_at.isoformat() if isinstance(question.updated_at, datetime) else question.updated_at
                
                return {
                    "total": len(questions),
                    "questions": questions
                }
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

        @api_router.put("/{question_id}", response_model=QuestionResponse)
        async def update_question(
            question_id: int,
            question: QuestionUpdate,
            db: Session = Depends(get_db)
        ):
            """
            Update an existing question.
            """
            try:
                domain = QuestionDomain(db)
                examples = [example.dict() for example in question.examples] if question.examples else None
                test_cases = [test_case.dict() for test_case in question.test_cases] if question.test_cases else None
                
                updated_question = domain.update_question(
                    question_id=question_id,
                    title=question.title,
                    description=question.description,
                    difficulty_level=question.difficulty_level,
                    examples=examples,
                    constraints=[str(constraint) for constraint in question.constraints],  # Convert constraints to strings
                    test_cases=test_cases
                )
                
                # Convert datetime fields to string
                updated_question.created_at = updated_question.created_at.isoformat() if isinstance(updated_question.created_at, datetime) else updated_question.created_at
                updated_question.updated_at = updated_question.updated_at.isoformat() if isinstance(updated_question.updated_at, datetime) else updated_question.updated_at

                return updated_question
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

        @api_router.delete("/{question_id}", status_code=204)
        async def delete_question(
            question_id: int,
            db: Session = Depends(get_db)
        ):
            """
            Delete a question.
            """
            try:
                domain = QuestionDomain(db)
                domain.delete_question(question_id)
                return None
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Internal server error")

        return api_router
