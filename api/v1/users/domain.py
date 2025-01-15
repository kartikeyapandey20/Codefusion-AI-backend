from .repository import UserRepository

class UserDomain:
    def __init__(self) -> None:
        self.__repository = UserRepository()
        
    def create_user(self, db, user):
        """
        Create a new user.

        Args:
            db: The database session.
            user: The data for the new user.

        Returns:
            User: The newly created user.
        """
        return self.__repository.create_user(user,db)
    
    def get_user_by_id(self, id, db):
        """
        Get a user by their ID.

        Args:
            id: The ID of the user.
            db: The database session.

        Returns:
            User: The user.
        """
        return self.__repository.get_user_by_id(id, db)
