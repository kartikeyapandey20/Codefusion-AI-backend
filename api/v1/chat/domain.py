from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import ChatRepository
from .schema import AIChatMessageCreate, AIChatMessageOut, ChatSessionOut, NewChatResponse
from utils.ai_utils import AIUtility
class ChatDomain:
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the Chat Domain with a database session.
        
        Args:
            db_session: Asynchronous SQLAlchemy session for database operations
        """
        self.chat_repository = ChatRepository(db_session)
        
        self.ai_utility = AIUtility()
    
    async def get_chat_history(self, session_id: int) -> List[AIChatMessageOut]:
        """
        Retrieve the full chat history for a specific session.
        
        Args:
            session_id: The unique identifier for the chat session
            
        Returns:
            List of chat messages in chronological order
        """
        return await self.chat_repository.get_chat_history(session_id)
    
    async def get_user_sessions(self, user_id: int) -> List[ChatSessionOut]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            List of chat sessions ordered by last activity
        """
        return await self.chat_repository.get_user_sessions(user_id)
    
    async def process_user_message(self, user_input: AIChatMessageCreate) -> AIChatMessageOut:
        """
        Process a user message and generate an AI response.
        
        Args:
            user_input: The user's message with session and user identifiers
            
        Returns:
            The AI's response message object
        """
        # Input validation
        if not user_input.message or not user_input.message.strip():
            raise ValueError("Message cannot be empty")
            
        return await self.chat_repository.chat_with_ai(user_input)
    
    async def start_new_chat(self, user_id: int, first_message: str) -> NewChatResponse:
        """
        Start a new chat session with the first message.
        
        Args:
            user_id: User's ID
            first_message: The first message from the user
            
        Returns:
            Object containing session_id and the AI's response
        """
        # Title generation using AIUtility
        
        session_title = self.ai_utility.generate_title(first_message)
        # Create new session
        session_id = await self.chat_repository.create_chat_session(user_id,session_title=session_title)
        
        # Create input object with the new session ID
        user_input = AIChatMessageCreate(
            session_id=session_id,
            user_id=user_id,
            message=first_message,
            role="user"
        )
        
        # Get AI response using existing method
        ai_response = await self.chat_repository.chat_with_ai(user_input)
        
        ai_response_out = AIChatMessageOut(
        id=ai_response.id,
        session_id=ai_response.session_id,
        user_id=ai_response.user_id,
        role=ai_response.role,
        message=ai_response.message,
        created_at=ai_response.created_at,
        session_title=session_title  # Add the session title
        )
        # Return both the session ID and response
        return NewChatResponse(
            session_id=session_id,
            message=ai_response_out
        )