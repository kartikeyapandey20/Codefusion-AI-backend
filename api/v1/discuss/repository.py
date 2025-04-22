from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, status
from .model import DiscussionThread, DiscussionMessage
from .schema import DiscussionMessageCreate, DiscussionThreadCreate

class DiscussionRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_discussion_thread(self, thread_data: DiscussionThreadCreate) -> DiscussionThread:
        """
        Create a new discussion thread for a question.
        """
        try:
            # Create a new thread entry
            new_thread = DiscussionThread(**thread_data.dict())
            self.db_session.add(new_thread)
            await self.db_session.commit()
            await self.db_session.refresh(new_thread)
            
            return new_thread
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create discussion thread: {str(e)}"
            )
    
    async def create_discussion_message(self, message_data: DiscussionMessageCreate) -> DiscussionMessage:
        """
        Create a new message in a discussion thread.
        """
        try:
            # Verify thread exists
            result = await self.db_session.execute(
                select(DiscussionThread).where(DiscussionThread.id == message_data.thread_id)
            )
            thread = result.scalars().first()
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Discussion thread not found"
                )
            
            # Create message
            new_message = DiscussionMessage(**message_data.dict())
            self.db_session.add(new_message)
            
            # Update thread's updated_at timestamp
            thread.updated_at = None  # Will trigger the onupdate function
            
            await self.db_session.commit()
            await self.db_session.refresh(new_message)
            
            return new_message
        except HTTPException:
            await self.db_session.rollback()
            raise
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create message: {str(e)}"
            )
    
    async def get_thread_messages(self, thread_id: int):
        """
        Get all messages in a discussion thread.
        """
        try:
            result = await self.db_session.execute(
                select(DiscussionMessage)
                .where(DiscussionMessage.thread_id == thread_id)
                .order_by(DiscussionMessage.created_at)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve messages: {str(e)}"
            )
    
    async def get_question_threads(self, question_id: int):
        """
        Get all discussion threads for a question.
        """
        try:
            result = await self.db_session.execute(
                select(DiscussionThread)
                .where(DiscussionThread.question_id == question_id)
                .order_by(DiscussionThread.updated_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve threads: {str(e)}"
            )
    
    async def get_user_threads(self, user_id: int):
        """
        Get all discussion threads created by a user.
        """
        try:
            result = await self.db_session.execute(
                select(DiscussionThread)
                .where(DiscussionThread.user_id == user_id)
                .order_by(DiscussionThread.updated_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve threads: {str(e)}"
            )
    
    async def get_thread_by_id(self, thread_id: int):
        """
        Get a discussion thread by its ID.
        """
        try:
            result = await self.db_session.execute(
                select(DiscussionThread).where(DiscussionThread.id == thread_id)
            )
            thread = result.scalars().first()
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Discussion thread not found"
                )
            return thread
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve thread: {str(e)}"
            )
            
    async def get_all_question_messages(self, question_id: int):
        """
        Get all discussion messages across all threads for a specific question.
        """
        try:
            # First get all threads for the question
            threads_result = await self.db_session.execute(
                select(DiscussionThread.id)
                .where(DiscussionThread.question_id == question_id)
            )
            thread_ids = [thread_id for thread_id, in threads_result]
            
            if not thread_ids:
                return []  # No threads found for this question
            
            # Then get all messages from those threads
            messages_result = await self.db_session.execute(
                select(DiscussionMessage)
                .where(DiscussionMessage.thread_id.in_(thread_ids))
                .order_by(DiscussionMessage.created_at)
            )
            
            return messages_result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve question messages: {str(e)}"
            )
