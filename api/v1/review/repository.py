from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from fastapi import HTTPException, status
import json
import google.generativeai as genai
from datetime import datetime
from .model import AIReview
from api.v1.submission.model import Submission
from .schema import AIReviewCreate, AIReviewUpdate, TestResult, AIReviewOut
from core.config import settings

class ReviewRepository:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Review Repository with a database session.
        """
        self.db_session = db_session
        # Configure Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def create_review(self, review_data: AIReviewCreate) -> AIReviewOut:
        """
        Create a new AI review for a submission.
        """
        try:
            # Check if submission exists
            result = await self.db_session.execute(
                select(Submission).where(Submission.id == review_data.submission_id)
            )
            submission = result.scalars().first()
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {review_data.submission_id} not found"
                )
            
            # Convert test_results to JSON string if provided
            test_results_json = None
            if review_data.test_results:
                test_results_json = json.dumps([t.dict() for t in review_data.test_results])
            
            # Create review
            db_review = AIReview(
                submission_id=review_data.submission_id,
                review_text=review_data.review_text,
                code_quality_score=review_data.code_quality_score,
                compliance_status=review_data.compliance_status,
                test_results=test_results_json,
                suggestions=review_data.suggestions,
                security_issues=review_data.security_issues,
                performance_notes=review_data.performance_notes
            )
            
            self.db_session.add(db_review)
            await self.db_session.commit()
            await self.db_session.refresh(db_review)
            
            # Update submission with test results and compliance status
            if review_data.test_results:
                submission.test_cases_passed = sum(1 for test in review_data.test_results if test.passed)
                submission.total_test_cases = len(review_data.test_results)
            
            submission.compliance_check = review_data.compliance_status or False
            await self.db_session.commit()
            
            return self._convert_to_response(db_review)
        
        except HTTPException as http_ex:
            await self.db_session.rollback()
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create review: {str(e)}"
            )
    
    async def get_review(self, review_id: int) -> AIReviewOut:
        """
        Get a review by ID.
        """
        try:
            result = await self.db_session.execute(
                select(AIReview).where(AIReview.id == review_id)
            )
            review = result.scalars().first()
            
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Review with ID {review_id} not found"
                )
            
            return self._convert_to_response(review)
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve review: {str(e)}"
            )
    
    async def get_reviews_by_submission(self, submission_id: int) -> list[AIReviewOut]:
        """
        Get all reviews for a submission.
        """
        try:
            result = await self.db_session.execute(
                select(AIReview)
                .where(AIReview.submission_id == submission_id)
                .order_by(AIReview.created_at.desc())
            )
            reviews = result.scalars().all()
            
            return [self._convert_to_response(review) for review in reviews]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve reviews: {str(e)}"
            )
    
    async def update_review(self, review_id: int, review_update: AIReviewUpdate) -> AIReviewOut:
        """
        Update an existing review.
        """
        try:
            # Check if review exists
            result = await self.db_session.execute(
                select(AIReview).where(AIReview.id == review_id)
            )
            review = result.scalars().first()
            
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Review with ID {review_id} not found"
                )
            
            # Update fields
            update_data = review_update.dict(exclude_unset=True)
            
            # Handle test_results separately if provided
            if 'test_results' in update_data and update_data['test_results'] is not None:
                update_data['test_results'] = json.dumps([t.dict() for t in update_data['test_results']])
            
            for key, value in update_data.items():
                setattr(review, key, value)
            
            await self.db_session.commit()
            await self.db_session.refresh(review)
            
            return self._convert_to_response(review)
        
        except HTTPException as http_ex:
            await self.db_session.rollback()
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update review: {str(e)}"
            )
    
    async def delete_review(self, review_id: int) -> bool:
        """
        Delete a review.
        """
        try:
            # Check if review exists
            result = await self.db_session.execute(
                select(AIReview).where(AIReview.id == review_id)
            )
            review = result.scalars().first()
            
            if not review:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Review with ID {review_id} not found"
                )
            
            await self.db_session.delete(review)
            await self.db_session.commit()
            
            return True
        
        except HTTPException as http_ex:
            await self.db_session.rollback()
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete review: {str(e)}"
            )
    
    async def generate_review_with_gemini(self, submission_id: int) -> AIReviewOut:
        """
        Generate an AI code review for a submission using Gemini.
        """
        try:
            # Get the submission
            result = await self.db_session.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalars().first()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            # Generate the review using Gemini
            review_text, code_quality_score, compliance_status, test_results, suggestions, security_issues, performance_notes = await self._analyze_code_with_gemini(
                submission.code, 
                submission.language or "python"
            )
            
            # Create the review
            review_data = AIReviewCreate(
                submission_id=submission_id,
                review_text=review_text,
                code_quality_score=code_quality_score,
                compliance_status=compliance_status,
                test_results=test_results,
                suggestions=suggestions,
                security_issues=security_issues,
                performance_notes=performance_notes
            )
            
            # Save to database using the create_review method
            return await self.create_review(review_data)
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate review: {str(e)}"
            )
    
    async def _analyze_code_with_gemini(self, code: str, language: str) -> tuple:
        """
        Analyze code using Gemini API and return structured review information.
        """
        # Prepare the prompt for code review
        prompt = f"""
        You are an expert code reviewer. Please analyze the following {language} code and provide a comprehensive review:
        
        ```{language}
        {code}
        ```
        
        Provide your analysis in the following format:
        
        1. Overall Review: A comprehensive review of the code.
        
        2. Code Quality Score: A score from 1-10 (10 being the best).
        
        3. Compliance Status: Whether the code passes basic compliance checks (true/false).
        
        4. Test Results: A list of test cases and whether they passed or failed.
        
        5. Improvement Suggestions: Specific suggestions for improving the code.
        
        6. Security Issues: Any security vulnerabilities or concerns.
        
        7. Performance Notes: Comments on code performance and efficiency.
        
        Format your response as a JSON object with these fields.
        """
        
        try:
            # Generate the response
            response = await self.model.generate_content_async(prompt)
            
            # Parse the JSON response
            # Extract the JSON part from the response
            response_text = response.text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start >= 0 and json_end >= 0:
                json_str = response_text[json_start:json_end+1]
                review_data = json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                review_data = {
                    "overall_review": response_text,
                    "code_quality_score": 5,
                    "compliance_status": False,
                    "test_results": [],
                    "improvement_suggestions": "",
                    "security_issues": "",
                    "performance_notes": ""
                }
            
            # Extract the data
            review_text = review_data.get("overall_review", "")
            code_quality_score = review_data.get("code_quality_score", 5)
            compliance_status = review_data.get("compliance_status", False)
            
            # Process test results
            test_results_raw = review_data.get("test_results", [])
            test_results = []
            for test in test_results_raw:
                test_results.append(TestResult(
                    test_name=test.get("name", "Unknown Test"),
                    passed=test.get("passed", False),
                    message=test.get("message", ""),
                    execution_time=test.get("execution_time")
                ))
            
            suggestions = review_data.get("improvement_suggestions", "")
            security_issues = review_data.get("security_issues", "")
            performance_notes = review_data.get("performance_notes", "")
            
            return review_text, code_quality_score, compliance_status, test_results, suggestions, security_issues, performance_notes
        
        except Exception as e:
            # Handle parsing errors
            return (
                f"Error generating structured review: {str(e)}. Raw response: {response.text if 'response' in locals() else 'No response generated'}",
                5,  # Default score
                False,  # Default compliance
                [],  # Empty test results
                "Could not generate suggestions due to parsing error",
                "Could not analyze security issues due to parsing error",
                "Could not analyze performance due to parsing error"
            )
    
    def _convert_to_response(self, db_review: AIReview) -> AIReviewOut:
        """
        Convert a database AIReview object to an AIReviewOut.
        """
        # Parse test_results JSON if available
        test_results = []
        if db_review.test_results:
            try:
                test_results_data = json.loads(db_review.test_results)
                for test_data in test_results_data:
                    test_results.append(TestResult(**test_data))
            except json.JSONDecodeError:
                # Handle invalid JSON
                pass
        
        return AIReviewOut(
            id=db_review.id,
            submission_id=db_review.submission_id,
            review_text=db_review.review_text,
            code_quality_score=db_review.code_quality_score,
            compliance_status=db_review.compliance_status,
            test_results=test_results,
            suggestions=db_review.suggestions,
            security_issues=db_review.security_issues,
            performance_notes=db_review.performance_notes,
            created_at=db_review.created_at
        )
