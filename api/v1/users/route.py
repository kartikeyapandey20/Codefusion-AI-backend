from fastapi import APIRouter, Depends, status
from .domain import UserDomain
from sqlalchemy.orm import Session
from core.deps import get_db
from .schema import UserSchema, UserOut

class UserRouter:
    def __init__(self) -> None:
        self.__domain = UserDomain()
        
    @property
    def router(self):
        """
        Get the API router for users.

        Returns:
            APIRouter: The API router.
        """
        api_router = APIRouter(prefix="/user", tags=["user"])
        
        @api_router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
        def create_user(user: UserSchema, db: Session = Depends(get_db)):
            """
            Create a new user.

            Args:
                user (UserSchema): The data for the new user.
                db (Session): The database session.

            Returns:
                UserOut: The newly created user.
            """
            return self.__domain.create_user(db, user) 

        @api_router.get("/{id}", response_model=UserOut)
        def get_users(id, db: Session = Depends(get_db)):
            """
            Get a user by their ID.

            Args:
                id: The ID of the user.
                db: The database session.

            Returns:
                UserOut: The user.
            """
            return self.__domain.get_user_by_id(id, db)
        
        return api_router
