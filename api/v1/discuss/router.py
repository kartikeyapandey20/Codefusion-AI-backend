from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .domain import DiscussDomain
from .schema import (
    DiscussionMessageCreate, 
    DiscussionMessageOut, 
    DiscussionThreadOut, 
    StartDiscussionRequest, 
    NewDiscussionResponse
)
from core.deps import get_async_db

class DiscussRouter:
    def __init__(self) -> None:
        pass
        
    @property
    def router(self):
        """
        Get the API router for discussion functionality.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(prefix="/discuss", tags=["Discussions"], responses={404: {"description": "Not found"}})
        
        @api_router.post("/start", response_model=NewDiscussionResponse)
        async def start_new_discussion(
            request: StartDiscussionRequest = Body(...),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Start a new discussion thread with the first message.
            
            Creates a new thread and adds the first message.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.start_new_discussion(request)
            
        @api_router.post("/message", response_model=DiscussionMessageOut)
        async def create_message(
            message_data: DiscussionMessageCreate = Body(...),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Add a new message to an existing discussion thread.
            
            Requires an existing thread_id.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.create_message(message_data)
            
        @api_router.get("/question/{question_id}", response_model=List[DiscussionThreadOut])
        async def get_question_threads(
            question_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all discussion threads for a specific question.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.get_question_threads(question_id)
            
        @api_router.get("/user/{user_id}", response_model=List[DiscussionThreadOut])
        async def get_user_threads(
            user_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all discussion threads created by a specific user.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.get_user_threads(user_id)
            
        @api_router.get("/thread/{thread_id}", response_model=List[DiscussionMessageOut])
        async def get_thread_messages(
            thread_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all messages in a specific discussion thread.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.get_thread_messages(thread_id)
        
        @api_router.get("/question/{question_id}/messages", response_model=List[DiscussionMessageOut])
        async def get_all_question_messages(
            question_id: int,
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get all discussion messages across all threads for a specific question.
            """
            discuss_domain = DiscussDomain(db)
            return await discuss_domain.get_all_question_messages(question_id)
            
        return api_router
