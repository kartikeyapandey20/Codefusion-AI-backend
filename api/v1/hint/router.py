from fastapi import APIRouter, Depends, Body, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .domain import HintDomain
from .schema import HintRequest, HintResponse, HintHistoryItem
from core.deps import get_async_db

class HintRouter:
    def __init__(self) -> None:
        pass
        
    @property
    def router(self):
        """
        Get the API router for hint functionality.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(prefix="/hint", tags=["Hints"], responses={404: {"description": "Not found"}})
        
        @api_router.post("/generate", response_model=HintResponse)
        async def generate_hint(
            request: HintRequest = Body(...),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Generate a hint for a specific question.
            
            The hint will provide guidance without giving away the complete solution.
            
            Args:
                request: Object containing user_id and question_id
                db: Database session
                
            Returns:
                HintResponse containing the generated hint and request details
            """
            hint_domain = HintDomain(db)
            return await hint_domain.get_hint(request)
        
        @api_router.get("/history/{user_id}", response_model=List[HintHistoryItem])
        async def get_hint_history(
            user_id: int,
            question_id: Optional[int] = Query(None, description="Filter history by question ID"),
            db: AsyncSession = Depends(get_async_db)
        ):
            """
            Get hint request history for a user.
            
            Optionally filter by question ID.
            
            Args:
                user_id: The user's ID
                question_id: Optional question ID to filter by
                db: Database session
                
            Returns:
                List of hint history items
            """
            hint_domain = HintDomain(db)
            return await hint_domain.get_user_hint_history(user_id, question_id)
            
        return api_router