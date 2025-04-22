from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import DiscussionRepository
from .schema import (
    DiscussionMessageCreate, 
    DiscussionMessageOut, 
    DiscussionThreadCreate, 
    DiscussionThreadOut,
    StartDiscussionRequest,
    NewDiscussionResponse
)

class DiscussDomain:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Discuss Domain with a database session.
        
        Args:
            db_session: Asynchronous SQLAlchemy session for database operations
        """
        self.discussion_repository = DiscussionRepository(db_session)
    
    async def get_thread_messages(self, thread_id: int) -> List[DiscussionMessageOut]:
        """
        Retrieve all messages in a discussion thread.
        
        Args:
            thread_id: The unique identifier for the discussion thread
            
        Returns:
            List of discussion messages in chronological order
        """
        return await self.discussion_repository.get_thread_messages(thread_id)
    
    async def get_question_threads(self, question_id: int) -> List[DiscussionThreadOut]:
        """
        Get all discussion threads for a question.
        
        Args:
            question_id: The question's unique identifier
            
        Returns:
            List of discussion threads ordered by last activity
        """
        return await self.discussion_repository.get_question_threads(question_id)
    
    async def get_user_threads(self, user_id: int) -> List[DiscussionThreadOut]:
        """
        Get all discussion threads created by a user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            List of discussion threads ordered by last activity
        """
        return await self.discussion_repository.get_user_threads(user_id)
        
    async def get_all_question_messages(self, question_id: int) -> List[DiscussionMessageOut]:
        """
        Get all discussion messages across all threads for a specific question.
        
        Args:
            question_id: The question's unique identifier
            
        Returns:
            List of all discussion messages for the question, ordered chronologically
        """
        return await self.discussion_repository.get_all_question_messages(question_id)
    
    async def create_message(self, message_data: DiscussionMessageCreate) -> DiscussionMessageOut:
        """
        Create a new message in a discussion thread.
        
        Args:
            message_data: The message data with thread_id, user_id, and content
            
        Returns:
            The created message object
        """
        # Input validation
        if not message_data.content or not message_data.content.strip():
            raise ValueError("Message content cannot be empty")
            
        return await self.discussion_repository.create_discussion_message(message_data)
    
    async def start_new_discussion(self, request: StartDiscussionRequest) -> NewDiscussionResponse:
        """
        Start a new discussion thread with the first message.
        
        Args:
            request: Object containing question_id, user_id, title, and initial message content
            
        Returns:
            Object containing the created thread and message
        """
        # Create thread
        thread_data = DiscussionThreadCreate(
            question_id=request.question_id,
            user_id=request.user_id,
            title=request.title
        )
        
        thread = await self.discussion_repository.create_discussion_thread(thread_data)
        
        # Create first message
        message_data = DiscussionMessageCreate(
            thread_id=thread.id,
            user_id=request.user_id,
            content=request.content
        )
        
        message = await self.discussion_repository.create_discussion_message(message_data)
        
        # Convert SQLAlchemy models to Pydantic models using Pydantic v2 approach
        thread_out = DiscussionThreadOut.model_validate(thread)
        message_out = DiscussionMessageOut.model_validate(message)
        
        # Return both the thread and message
        return NewDiscussionResponse(
            thread=thread_out,
            message=message_out
        )
