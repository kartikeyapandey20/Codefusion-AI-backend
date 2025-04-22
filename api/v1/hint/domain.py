from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import HintRepository
from .schema import HintRequest, HintResponse, HintHistoryItem

class HintDomain:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Hint Domain with a database session.
        
        Args:
            db_session: Asynchronous SQLAlchemy session for database operations
        """
        self.hint_repository = HintRepository(db_session)
    
    async def get_hint(self, request: HintRequest) -> HintResponse:
        """
        Process a hint request and generate a hint for the specified question.
        
        Args:
            request: The hint request containing user_id and question_id
            
        Returns:
            HintResponse object containing the generated hint and request details
        """
        # Create a hint request record
        hint_request = await self.hint_repository.create_hint_request(
            user_id=request.user_id,
            question_id=request.question_id
        )
        
        # Get the question details
        question = await self.hint_repository.get_question_by_id(request.question_id)
        
        # Generate the hint
        hint_text = await self.hint_repository.generate_hint(question)
        
        # Return the response
        return HintResponse(
            hint=hint_text,
            request_id=hint_request.id,
            question_id=hint_request.question_id,
            user_id=hint_request.user_id,
            request_time=hint_request.request_time
        )
    
    async def get_user_hint_history(self, user_id: int, question_id: Optional[int] = None) -> List[HintHistoryItem]:
        """
        Get hint request history for a user, optionally filtered by question.
        
        Args:
            user_id: The user's ID
            question_id: Optional question ID to filter by
            
        Returns:
            List of hint history items
        """
        # Get hint history from repository
        hint_requests = await self.hint_repository.get_hint_history(user_id, question_id)
        
        # For a real implementation, you would need to store the generated hints
        # This is a simplified version that doesn't include the actual hint text
        return [
            HintHistoryItem(
                id=req.id,
                question_id=req.question_id,
                user_id=req.user_id,
                request_time=req.request_time,
                hint="Hint data not stored in this version"  # In a real implementation, you would store and retrieve the actual hint
            )
            for req in hint_requests
        ]