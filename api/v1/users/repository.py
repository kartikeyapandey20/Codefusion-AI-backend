from api.v1.users.model import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from core.deps import get_db
from .schema import UserSchema
from passlib.context import CryptContext
from core.security import hash_password

class UserRepository:
    def create_user(self, user: UserSchema, db: Session = Depends(get_db)):
        """
        Create a new user.

        Args:
            user (UserSchema): The data for the new user.
            db (Session): The SQLAlchemy database session.

        Returns:
            User: The newly created user.
        """
        hashed_password = hash_password(user.password)
        user.password = hashed_password
        
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    def get_user_by_id(self, id: int, db: Session = Depends(get_db)):
        """
        Get a user by their ID.

        Args:
            id (int): The ID of the user.
            db (Session): The SQLAlchemy database session.

        Raises:
            HTTPException: If the user is not found.

        Returns:
            User: The user.
        """
        user = db.query(User).filter(User.id == id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return user
