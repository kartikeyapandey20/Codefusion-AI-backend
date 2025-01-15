from .repository import AuthenticationRepository

class AuthenticationDomain:
    def __init__(self) -> None:
        self.__repository = AuthenticationRepository()
        
    def login(self, user_credentials, db):
        """
        Log in a user.

        Args:
            user_credentials: The user's login credentials.
            db: The database session.

        Returns:
            dict: The access token and its type.
        """
        return self.__repository.login(user_credentials, db)
