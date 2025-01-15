from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.deps import get_db
from .domain import AuthenticationDomain
from .schema import TokenResponse

class AuthenticationRouter:
    def __init__(self) -> None:
        self.__domain = AuthenticationDomain()
    
    @property
    def router(self):
        """
        Get the API router for authentication.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(prefix="/login", tags=["login"])
        
        @api_router.post("/", status_code=status.HTTP_200_OK, response_model=TokenResponse)
        def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
            """
            Log in a user.

            Args:
                user_credentials (OAuth2PasswordRequestForm): The user's login credentials.
                db (Session): The SQLAlchemy database session.

            Returns:
                TokenResponse: The access token and its type.
            """
            return self.__domain.login(user_credentials, db)

        return api_router
