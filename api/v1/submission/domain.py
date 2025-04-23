from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import json
from .repository import SubmissionRepository
from .schema import SubmissionCreate, SubmissionUpdate, SubmissionOut, SubmissionWithReviews, SubmitAndReviewResponse
from api.v1.question.domain import QuestionDomain

class SubmissionDomain:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Submission Domain with a database session.
        
        Args:
            db_session: Asynchronous SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self.submission_repository = SubmissionRepository(db_session)
        self.question_domain = QuestionDomain(db_session)
    
    async def create_submission(self, submission_data: SubmissionCreate) -> SubmissionOut:
        """
        Create a new code submission.
        
        Args:
            submission_data: The submission data to create
            
        Returns:
            The created submission
        """
        return await self.submission_repository.create_submission(submission_data)
    
    async def get_submission(self, submission_id: int) -> SubmissionOut:
        """
        Get a submission by ID.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            The submission details
        """
        return await self.submission_repository.get_submission(submission_id)
    
    async def get_submission_with_reviews(self, submission_id: int) -> SubmissionWithReviews:
        """
        Get a submission with all its reviews.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            The submission with its reviews
        """
        return await self.submission_repository.get_submission_with_reviews(submission_id)
    
    async def get_submissions_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[SubmissionOut]:
        """
        Get all submissions for a user.
        
        Args:
            user_id: The unique identifier for the user
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of submissions for the user
        """
        return await self.submission_repository.get_submissions_by_user(user_id, skip, limit)
    
    async def get_submissions_by_question(self, question_id: int, skip: int = 0, limit: int = 100) -> List[SubmissionOut]:
        """
        Get all submissions for a question.
        
        Args:
            question_id: The unique identifier for the question
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            
        Returns:
            List of submissions for the question
        """
        return await self.submission_repository.get_submissions_by_question(question_id, skip, limit)
    
    async def update_submission(self, submission_id: int, submission_update: SubmissionUpdate) -> SubmissionOut:
        """
        Update an existing submission.
        
        Args:
            submission_id: The unique identifier for the submission
            submission_update: The data to update
            
        Returns:
            The updated submission
        """
        return await self.submission_repository.update_submission(submission_id, submission_update)
    
    async def compile_submission(self, submission_id: int) -> SubmissionOut:
        """
        Compile and run a submission's code using LLM.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            The updated submission with compilation results
        """
        try:
            # Get submission details
            submission = await self.get_submission(submission_id)
            
            # Get question details
            question = await self.question_domain.get_question(submission.question_id)
            
            # Convert question to dict for easy handling
            question_data = {
                "id": question.id,
                "title": question.title,
                "description": question.description,
                "difficulty_level": question.difficulty_level,
                "examples": question.examples,
                "constraints": question.constraints,
                "test_cases": question.test_cases
            }
            
            # Compile the code
            return await self.submission_repository.compile_code(submission_id, question_data)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to compile submission: {str(e)}"
            )
    
    async def get_code_recommendations(self, submission_id: int) -> Dict[str, Any]:
        """
        Get AI-powered code recommendations for a submission.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            Dictionary containing code recommendations and improvements
        """
        try:
            # Get submission details
            submission = await self.get_submission(submission_id)
            
            # Get question details
            question = await self.question_domain.get_question(submission.question_id)
            
            # Convert question to dict for easy handling
            question_data = {
                "id": question.id,
                "title": question.title,
                "description": question.description,
                "difficulty_level": question.difficulty_level,
                "examples": question.examples,
                "constraints": question.constraints,
                "test_cases": question.test_cases
            }
            
            # Get recommendations
            return await self.submission_repository.get_code_recommendations(submission_id, question_data)
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get code recommendations: {str(e)}"
            )
    
    async def submit_and_review(self, submission_data: SubmissionCreate) -> SubmitAndReviewResponse:
        """
        Create a submission, compile it, and generate recommendations in one step.
        
        Args:
            submission_data: The submission data to create
            
        Returns:
            Object containing the submission ID and review information
        """
        try:
            # Create the submission
            submission = await self.create_submission(submission_data)
            
            # Compile the submission
            await self.compile_submission(submission.id)
            
            # Generate recommendations
            recommendations = await self.get_code_recommendations(submission.id)
            
            # Get the submission with its reviews
            submission_with_reviews = await self.get_submission_with_reviews(submission.id)
            
            # Return the review info
            latest_review = submission_with_reviews.ai_reviews[0] if submission_with_reviews.ai_reviews else None
            
            return SubmitAndReviewResponse(
                submission_id=submission.id,
                review=latest_review
            )
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit and review code: {str(e)}"
            )