from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, and_
from fastapi import HTTPException, status
import json
from datetime import datetime
import google.generativeai as genai
from .model import Submission
from api.v1.review.model import AIReview
from .schema import SubmissionCreate, SubmissionUpdate, SubmissionOut, SubmissionWithReviews
from api.v1.review.schema import AIReviewOut
from core.config import settings

class SubmissionRepository:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Submission Repository with a database session.
        """
        self.db_session = db_session
        # Configure the Gemini API with your API key
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def create_submission(self, submission_data: SubmissionCreate) -> SubmissionOut:
        """
        Create a new code submission.
        """
        try:
            # Create submission
            db_submission = Submission(
                user_id=submission_data.user_id,
                question_id=submission_data.question_id,
                code=submission_data.code,
                language=submission_data.language,
                result=None,
                test_cases_passed=0,
                total_test_cases=0,
                compliance_check=False
            )
            
            self.db_session.add(db_submission)
            await self.db_session.commit()
            await self.db_session.refresh(db_submission)
            
            return SubmissionOut.from_orm(db_submission)
        
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create submission: {str(e)}"
            )
    
    async def get_submission(self, submission_id: int) -> SubmissionOut:
        """
        Get a submission by ID.
        """
        try:
            result = await self.db_session.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalars().first()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            return SubmissionOut.from_orm(submission)
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve submission: {str(e)}"
            )
    
    async def get_submission_with_reviews(self, submission_id: int) -> SubmissionWithReviews:
        """
        Get a submission with all its reviews.
        """
        try:
            # Get submission
            result = await self.db_session.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalars().first()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            # Get reviews for this submission
            reviews_result = await self.db_session.execute(
                select(AIReview)
                .where(AIReview.submission_id == submission_id)
                .order_by(AIReview.created_at.desc())
            )
            reviews = reviews_result.scalars().all()
            
            # Convert reviews to response objects
            review_responses = [AIReviewOut.from_orm(review) for review in reviews]
            
            # Create response with submission and reviews
            response = SubmissionWithReviews.from_orm(submission)
            response.ai_reviews = review_responses
            
            return response
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve submission with reviews: {str(e)}"
            )
    
    async def get_submissions_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[SubmissionOut]:
        """
        Get all submissions for a user with pagination.
        """
        try:
            result = await self.db_session.execute(
                select(Submission)
                .where(Submission.user_id == user_id)
                .order_by(Submission.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()
            
            return [SubmissionOut.from_orm(submission) for submission in submissions]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve submissions: {str(e)}"
            )
    
    async def get_submissions_by_question(self, question_id: int, skip: int = 0, limit: int = 100) -> list[SubmissionOut]:
        """
        Get all submissions for a question with pagination.
        """
        try:
            result = await self.db_session.execute(
                select(Submission)
                .where(Submission.question_id == question_id)
                .order_by(Submission.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            submissions = result.scalars().all()
            
            return [SubmissionOut.from_orm(submission) for submission in submissions]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve submissions: {str(e)}"
            )
    
    async def update_submission(self, submission_id: int, submission_update: SubmissionUpdate) -> SubmissionOut:
        """
        Update an existing submission.
        """
        try:
            # Check if submission exists
            result = await self.db_session.execute(
                select(Submission).where(Submission.id == submission_id)
            )
            submission = result.scalars().first()
            
            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Submission with ID {submission_id} not found"
                )
            
            # Update fields
            update_data = submission_update.dict(exclude_unset=True)
            
            for key, value in update_data.items():
                setattr(submission, key, value)
            
            # Update updated_at timestamp
            submission.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            await self.db_session.refresh(submission)
            
            return SubmissionOut.from_orm(submission)
        
        except HTTPException as http_ex:
            await self.db_session.rollback()
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update submission: {str(e)}"
            )
    
    async def compile_code(self, submission_id: int, question_data: dict) -> SubmissionOut:
        """
        Compile and run code using Gemini API, updating submission with results.
        
        Args:
            submission_id: ID of the submission to compile
            question_data: Data about the question including test cases
            
        Returns:
            Updated submission with compilation results
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
            
            # Create system and user prompts
            system_prompt = """You are a precise code execution engine. Your task is to execute the provided code against the test cases and provide accurate results.
            
            You must execute the code exactly as written and provide the results in a structured JSON format.
            Do not provide explanations or suggestions - only execute the code and report the results.
            
            For each test case, you should:
            1. Run the code with the input
            2. Compare the actual output with the expected output
            3. Report whether the test case passed or failed
            
            Format your response ONLY as a valid JSON object with the following structure:
            {
                "test_results": [
                    {
                        "test_case_id": 1,
                        "input": "the input that was provided",
                        "expected_output": "the expected output",
                        "actual_output": "the actual output from the code",
                        "passed": true/false,
                        "error": "any error message if applicable"
                    },
                    ... additional test cases ...
                ],
                "summary": {
                    "total_tests": 5,
                    "passed": 3,
                    "failed": 2
                }
            }
            
            Make sure your JSON is correctly formatted and parseable."""
            
            # Format test cases for the prompt
            test_cases = question_data.get("test_cases", [])
            formatted_test_cases = json.dumps(test_cases, indent=2)
            
            # Create the user prompt
            user_prompt = f"""
            Code ({submission.language}):
            ```{submission.language}
            {submission.code}
            ```
            
            Test Cases:
            {formatted_test_cases}
            """
            
            # Call the Gemini API
            response = await self._generate_async(system_prompt, user_prompt)
            
            # Parse the result
            try:
                result_json = json.loads(response)
            except json.JSONDecodeError:
                # Attempt to extract JSON if full response isn't valid JSON
                import re
                json_match = re.search(r'({[\s\S]*})', response)
                if json_match:
                    try:
                        result_json = json.loads(json_match.group(1))
                    except:
                        result_json = {"test_results": [], "summary": {"total_tests": 0, "passed": 0, "failed": 0}}
                else:
                    result_json = {"test_results": [], "summary": {"total_tests": 0, "passed": 0, "failed": 0}}
            
            # Update submission with results
            summary = result_json.get("summary", {})
            total_tests = summary.get("total_tests", len(result_json.get("test_results", [])))
            passed_tests = summary.get("passed", 0)
            
            submission.total_test_cases = total_tests
            submission.test_cases_passed = passed_tests
            
            # Determine result based on passed tests
            if total_tests > 0:
                pass_rate = passed_tests / total_tests
                if pass_rate == 1.0:
                    submission.result = "Accepted"
                elif pass_rate >= 0.8:
                    submission.result = "Partially Accepted"
                else:
                    submission.result = "Failed"
            else:
                submission.result = "Error"
            
            # Store the full test results in a review
            from api.v1.review.model import AIReview
            test_results_review = AIReview(
                submission_id=submission.id,
                review_type="test_results",
                content="Code execution results",
                test_results=json.dumps(result_json),
                score=None
            )
            
            self.db_session.add(test_results_review)
            await self.db_session.commit()
            await self.db_session.refresh(submission)
            
            return SubmissionOut.from_orm(submission)
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to compile code: {str(e)}"
            )
    
    async def get_code_recommendations(self, submission_id: int, question_data: dict) -> dict:
        """
        Generate code recommendations using Gemini API for an existing submission.
        
        Args:
            submission_id: ID of the submission to analyze
            question_data: Data about the question including description and constraints
            
        Returns:
            Dictionary with code recommendations and improvement insights
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
            
            # Create system prompt
            system_prompt = """You are an expert code reviewer specializing in algorithmic optimization and best practices.
            
            Analyze the provided code solution for the given algorithmic problem, and provide comprehensive recommendations focusing on:
            
            1. Time and Space Complexity: Analyze the current complexity and suggest optimizations.
            2. Code Readability: Suggest improvements for variable naming, comments, and structure.
            3. Performance Bottlenecks: Identify and suggest fixes for inefficient code patterns.
            4. Alternative Approaches: Suggest 1-2 different algorithmic approaches if applicable.
            5. Edge Cases: Point out any unhandled edge cases.
            
            Format your response as a JSON object with the following structure:
            {
                "complexity_analysis": {
                    "current_time": "O(n^2)",
                    "current_space": "O(n)",
                    "optimized_time": "O(n log n)",
                    "optimized_space": "O(n)"
                },
                "key_observations": [
                    "Observation 1",
                    "Observation 2"
                ],
                "improvement_suggestions": [
                    {
                        "issue": "Description of the issue",
                        "recommendation": "Specific recommendation",
                        "code_example": "Example code snippet (if applicable)"
                    }
                ],
                "alternative_approaches": [
                    {
                        "name": "Approach name",
                        "description": "Brief description",
                        "advantages": ["advantage 1", "advantage 2"],
                        "code_snippet": "Sample code implementing this approach"
                    }
                ],
                "overall_assessment": "Summary assessment of the solution"
            }
            
            Make sure your JSON is correctly formatted and parseable."""
            
            # Format the problem context for the prompt
            user_prompt = f"""
            Problem:
            Title: {question_data.get('title', 'Unknown Problem')}
            Description: {question_data.get('description', 'No description available')}
            
            Constraints:
            {json.dumps(question_data.get('constraints', []), indent=2)}
            
            Examples:
            {json.dumps(question_data.get('examples', []), indent=2)}
            
            Submitted Code ({submission.language}):
            ```{submission.language}
            {submission.code}
            ```
            
            Current Results:
            - Tests Passed: {submission.test_cases_passed}/{submission.total_test_cases}
            - Result: {submission.result}
            """
            
            # Call the Gemini API
            response = await self._generate_async(system_prompt, user_prompt)
            
            # Parse the recommendation result
            try:
                recommendations = json.loads(response)
            except json.JSONDecodeError:
                # Attempt to extract JSON if full response isn't valid JSON
                import re
                json_match = re.search(r'({[\s\S]*})', response)
                if json_match:
                    try:
                        recommendations = json.loads(json_match.group(1))
                    except:
                        recommendations = {"error": "Failed to parse recommendations"}
                else:
                    recommendations = {"error": "Failed to parse recommendations"}
            
            # Store the recommendations in a review
            from api.v1.review.model import AIReview
            recommendation_review = AIReview(
                submission_id=submission.id,
                review_type="recommendation",
                content=json.dumps(recommendations),
                test_results=None,
                score=None
            )
            
            self.db_session.add(recommendation_review)
            await self.db_session.commit()
            
            return recommendations
        
        except HTTPException as http_ex:
            raise http_ex
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate code recommendations: {str(e)}"
            )
    
    async def _generate_async(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using the Gemini API asynchronously.
        
        Args:
            system_prompt: The system prompt to guide the model
            user_prompt: The user prompt containing the content
            
        Returns:
            The generated text response
        """
        try:
            # For Google's API, combine the system and user prompts
            chat = self.model.start_chat(history=[
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["I understand and will follow these instructions."]}
            ])
            
            # In a real implementation, you would use an async version of the generate_content
            # Since the google-generativeai library doesn't have async support built-in yet,
            # you'd need to use asyncio.to_thread or similar to prevent blocking
            import asyncio
            response = await asyncio.to_thread(
                chat.send_message,
                user_prompt
            )
            
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate from Gemini API: {str(e)}")