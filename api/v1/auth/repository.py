from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.deps import get_db
from .schema import UserLogin
from ..users.model import User
from core.security import verify_password
from .oauth2 import create_access_token, get_current_user

class AuthenticationRepository: 
    def login(self, user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
        """
        Log in a user.

        Args:
            user_credentials (OAuth2PasswordRequestForm): The user's login credentials.
            db (Session): The SQLAlchemy database session.

        Raises:
            HTTPException: If the username or password is invalid.

        Returns:
            dict: The access token and its type.
        """
        user = db.query(User).filter(User.email == user_credentials.username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid username or password"
            )
            
        if not verify_password(user_credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid username or password"
            )
            
        access_token = create_access_token(data={"user_id": user.id})
        return {"access_token": access_token, "token_type": "bearer" , "user_id": user.id}
