from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .domain import ChatDomain
from .schema import AIChatMessageCreate, AIChatMessageOut, ChatSessionOut, StartChatRequest, NewChatResponse ,ChatMessageOut
from core.deps import get_async_db

class ChatRouter:
    def __init__(self) -> None:
        pass
        
    @property
    def router(self):
        """
        Get the API router for chat functionality.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(prefix="/chat", tags=["Chat"], responses={404: {"description": "Not found"}})
        
        @api_router.post("/start", response_model=NewChatResponse)
        async def start_new_chat(
            request: StartChatRequest = Body(...),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Start a new chat session with the first message.
            
            Creates a new session and processes the first message.
            """
            chat_domain = ChatDomain(db)
            return await chat_domain.start_new_chat(request.user_id, request.message)
            
        @api_router.post("/message", response_model=ChatMessageOut)
        async def send_message(
            chat_input: AIChatMessageCreate = Body(...),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Send a message to an existing chat session.
            
            Requires an existing session_id.
            """
            chat_domain = ChatDomain(db)
            return await chat_domain.process_user_message(chat_input)
            
        @api_router.get("/sessions/{user_id}", response_model=List[ChatSessionOut])
        async def get_user_sessions(
            user_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all chat sessions for a user.
            """
            chat_domain = ChatDomain(db)
            return await chat_domain.get_user_sessions(user_id)
            
        @api_router.get("/history/{session_id}")
        async def get_chat_history(
            session_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get the full history of messages for a chat session.
            """
            chat_domain = ChatDomain(db)
            return await chat_domain.get_chat_history(session_id)
            
        return api_router