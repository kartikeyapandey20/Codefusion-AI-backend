from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from .domain import SubmissionDomain
from .schema import (
    SubmissionCreate, 
    SubmissionUpdate, 
    SubmissionOut, 
    SubmissionWithReviews,
    SubmitAndReviewResponse,
    CodeSubmitRequest
)
from core.deps import get_async_db

class SubmissionRouter:
    def __init__(self) -> None:
        self.tags = ["Submissions"]
    
    @property
    def router(self):
        """
        Get the API router for submissions.
        
        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(
            prefix="/submissions",
            tags=self.tags,
            responses={
                404: {"description": "Not found"},
                400: {"description": "Bad request"},
                500: {"description": "Internal server error"}
            }
        )
        
        @api_router.post("/", response_model=SubmissionOut, status_code=201)
        async def create_submission(
            submission_data: SubmissionCreate,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Create a new code submission.
            """
            try:
                domain = SubmissionDomain(db)
                return await domain.create_submission(submission_data)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=str(e)
                )
        
        @api_router.get("/{submission_id}", response_model=SubmissionOut)
        async def get_submission(
            submission_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get a specific submission by ID.
            """
            domain = SubmissionDomain(db)
            return await domain.get_submission(submission_id)
        
        @api_router.get("/{submission_id}/with-reviews", response_model=SubmissionWithReviews)
        async def get_submission_with_reviews(
            submission_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get a submission with all its AI reviews.
            """
            domain = SubmissionDomain(db)
            return await domain.get_submission_with_reviews(submission_id)
        
        @api_router.get("/user/{user_id}", response_model=List[SubmissionOut])
        async def get_submissions_by_user(
            user_id: int,
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=1000),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all submissions for a user with pagination.
            """
            domain = SubmissionDomain(db)
            return await domain.get_submissions_by_user(user_id, skip, limit)
        
        @api_router.get("/question/{question_id}", response_model=List[SubmissionOut])
        async def get_submissions_by_question(
            question_id: int,
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=1000),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all submissions for a question with pagination.
            """
            domain = SubmissionDomain(db)
            return await domain.get_submissions_by_question(question_id, skip, limit)
        
        @api_router.put("/{submission_id}", response_model=SubmissionOut)
        async def update_submission(
            submission_id: int,
            submission_update: SubmissionUpdate,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Update a submission.
            """
            domain = SubmissionDomain(db)
            return await domain.update_submission(submission_id, submission_update)
        
        @api_router.post("/compile/{submission_id}", response_model=SubmissionOut)
        async def compile_submission(
            submission_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Compile and run the code for a submission using LLM.
            """
            domain = SubmissionDomain(db)
            return await domain.compile_submission(submission_id)
        
        @api_router.post("/recommend/{submission_id}", response_model=Dict[str, Any])
        async def get_recommendations(
            submission_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get AI-powered recommendations for code improvement.
            """
            domain = SubmissionDomain(db)
            return await domain.get_code_recommendations(submission_id)
        
        @api_router.post("/submit-and-review", response_model=SubmitAndReviewResponse)
        async def submit_and_review(
            code_request: CodeSubmitRequest,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Submit code, compile it and get AI review in a single API call.
            """
            submission_data = SubmissionCreate(
                user_id=code_request.user_id,
                question_id=code_request.question_id,
                code=code_request.code,
                language=code_request.language
            )
            
            domain = SubmissionDomain(db)
            return await domain.submit_and_review(submission_data)
        
        return api_router