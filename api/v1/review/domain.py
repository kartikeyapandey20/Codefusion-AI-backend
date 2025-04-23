from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import json
import google.generativeai as genai
from .repository import ReviewRepository
from .schema import AIReviewCreate, AIReviewResponse, TestResult
from api.v1.submission.schema import SubmissionResponse
from core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

class ReviewDomain:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Review Domain with a database session.
        
        Args:
            db_session: Asynchronous SQLAlchemy session for database operations
        """
        self.review_repository = ReviewRepository(db_session)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def get_review(self, review_id: int) -> AIReviewResponse:
        """
        Get a review by ID.
        
        Args:
            review_id: The unique identifier for the review
            
        Returns:
            The review details
        """
        return await self.review_repository.get_review(review_id)
    
    async def get_reviews_by_submission(self, submission_id: int) -> List[AIReviewResponse]:
        """
        Get all reviews for a submission.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            List of reviews for the submission
        """
        return await self.review_repository.get_reviews_by_submission(submission_id)
    
    async def create_review(self, review_data: AIReviewCreate) -> AIReviewResponse:
        """
        Create a new AI review for a submission.
        
        Args:
            review_data: The review data to create
            
        Returns:
            The created review
        """
        return await self.review_repository.create_review(review_data)
    
    async def generate_review(self, submission_id: int) -> AIReviewResponse:
        """
        Generate an AI code review for a submission using Gemini.
        
        Args:
            submission_id: The unique identifier for the submission
            
        Returns:
            The generated review
        """
        return await self.review_repository.generate_review_with_gemini(submission_id)
    
    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using Gemini API and return structured review information.
        
        Args:
            code: The code to analyze
            language: The programming language of the code
            
        Returns:
            Dictionary containing the analysis results
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
            
            return review_data
        
        except Exception as e:
            # Handle parsing errors
            return {
                "overall_review": f"Error generating structured review: {str(e)}",
                "code_quality_score": 5,
                "compliance_status": False,
                "test_results": [],
                "improvement_suggestions": "Could not generate suggestions due to parsing error",
                "security_issues": "Could not analyze security issues due to parsing error",
                "performance_notes": "Could not analyze performance due to parsing error"
            }
