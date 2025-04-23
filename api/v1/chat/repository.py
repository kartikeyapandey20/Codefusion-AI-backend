from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from fastapi import HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI
from .model import AIChatMessage, ChatSession
from .schema import AIChatMessageCreate, AIChatMessageOut
from datetime import datetime
from fastapi import Depends
class ChatRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # Configure LangChain Gemini wrapper (Gemini-2-Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            convert_system_message_to_human=True  
        )

    async def create_chat_session(self, user_id: int,session_title:str) -> int:
        """
        Create a new chat session for a user.
        """
        try:
            # Create a new session entry
            new_session = ChatSession(user_id=user_id,session_title=session_title)
            self.db_session.add(new_session)
            await self.db_session.commit()
            await self.db_session.refresh(new_session)
            
            return new_session.id
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create session: {str(e)}"
            )

    async def get_chat_history(self, session_id: int):
        """
        Get chat history for a session.
        """
        try:
            result = await self.db_session.execute(
                select(AIChatMessage)
                .where(AIChatMessage.session_id == session_id)
                .order_by(AIChatMessage.created_at)
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve messages: {str(e)}"
            )

    async def get_user_sessions(self, user_id: int):
        """
        Get all chat sessions for a user.
        """
        try:
            result = await self.db_session.execute(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.last_active.desc())
            )
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve sessions: {str(e)}"
            )

    async def update_session_activity(self, session_id: int):
        """
        Update the last active timestamp for a session.
        """
        try:
            result = await self.db_session.execute(
                select(ChatSession).where(ChatSession.id == session_id)
            )
            session = result.scalars().first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            
            session.last_active = datetime.now()
            await self.db_session.commit()
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update session: {str(e)}"
            )

    async def chat_with_ai(self, user_input: AIChatMessageCreate) -> AIChatMessageOut:
        """
        Handle chat: store user message, get AI response from Gemini, store AI response.
        """
        try:
            # Update session activity
            await self.update_session_activity(user_input.session_id)
            
            # 1. Store user message
            user_msg = AIChatMessage(**user_input.dict())
            self.db_session.add(user_msg)
            await self.db_session.commit()
            await self.db_session.refresh(user_msg)

            # 2. Build conversation history for Gemini context
            chat_history = await self.get_chat_history(session_id=user_input.session_id)
            
            # Create system prompt
            system_prompt = {
                "role": "system", 
                "content": """You are a helpful coding assistant for programmers. 
                - Provide concise, practical solutions to coding problems
                - Include code examples with explanations
                - When appropriate, explain algorithm complexity (time/space)
                - If you're unsure about something, acknowledge it instead of guessing
                - Format code blocks properly using markdown syntax
                - Focus on best practices and performance considerations
                """
            }
            
            # Build history with system prompt first
            langchain_history = [system_prompt]
            langchain_history.extend([
                {"role": m.role, "content": m.message} for m in chat_history
            ])
            
            # Add current user message
            langchain_history.append({"role": "user", "content": user_input.message})

            # 3. Get response from Gemini
            response = self.llm.invoke(langchain_history)

            # 4. Store AI message
            ai_msg = AIChatMessage(
                session_id=user_input.session_id,
                user_id=user_input.user_id,
                role="ai",
                message=response.content
            )
            self.db_session.add(ai_msg)
            await self.db_session.commit()
            await self.db_session.refresh(ai_msg)

            return ai_msg

        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat failed: {str(e)}"
            )
