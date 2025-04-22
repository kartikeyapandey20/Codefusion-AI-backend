from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .model import AIHintRequest
from api.v1.question.model import Question
from typing import Dict, Any

class HintRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # Configure LangChain Gemini wrapper
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.5,  # Lower temperature for more focused hints
        )
        
        # Create the hint generation prompt template
        self.hint_prompt = PromptTemplate(
            input_variables=["question_title", "question_description", "difficulty"],
            template="""You are a helpful programming tutor who provides hints for coding problems. 
            Your goal is to guide the student toward the solution without giving away the complete answer.
            
            The student is working on a problem with the following details:
            Title: {question_title}
            Description: {question_description}
            Difficulty: {difficulty}
            
            Provide a helpful hint that:
            1. Identifies a key concept or approach needed to solve the problem
            2. Offers a small nudge in the right direction without revealing the full solution
            3. Encourages critical thinking
            4. Is concise (maximum 3-4 sentences)
            5. Includes a thought-provoking question to help the student think through the problem
            
            Your hint should be specific to the problem but not give away the solution algorithm or code.
            Format your response as a single paragraph without any introductory text like 'Here's a hint:'"""
        )
        
        # Create the LLMChain for hint generation
        self.hint_chain = LLMChain(llm=self.llm, prompt=self.hint_prompt)
    
    async def get_question_by_id(self, question_id: int) -> Question:
        """Get question details by ID"""
        try:
            result = await self.db_session.execute(
                select(Question).where(Question.id == question_id)
            )
            question = result.scalars().first()
            if not question:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Question not found"
                )
            return question
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve question: {str(e)}"
            )
    
    async def create_hint_request(self, user_id: int, question_id: int) -> AIHintRequest:
        """Create a new hint request record"""
        try:
            # First check if the question exists
            await self.get_question_by_id(question_id)
            
            # Create hint request
            hint_request = AIHintRequest(user_id=user_id, question_id=question_id)
            self.db_session.add(hint_request)
            await self.db_session.commit()
            await self.db_session.refresh(hint_request)
            
            return hint_request
        except HTTPException:
            await self.db_session.rollback()
            raise
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create hint request: {str(e)}"
            )
    
    async def generate_hint(self, question: Question) -> str:
        """Generate a hint for the given question using LangChain and Gemini"""
        try:
            # Prepare the input for the hint chain
            hint_input = {
                "question_title": question.title,
                "question_description": question.description,
                "difficulty": question.difficulty
            }
            
            # Generate the hint
            result = await self.hint_chain.arun(hint_input)
            
            return result.strip()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate hint: {str(e)}"
            )
    
    async def get_hint_history(self, user_id: int, question_id: int = None):
        """Get hint request history for a user, optionally filtered by question"""
        try:
            query = select(AIHintRequest).where(AIHintRequest.user_id == user_id)
            
            if question_id is not None:
                query = query.where(AIHintRequest.question_id == question_id)
            
            query = query.order_by(AIHintRequest.request_time.desc())
            
            result = await self.db_session.execute(query)
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve hint history: {str(e)}"
            )