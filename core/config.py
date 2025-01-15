import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Consists of system wide configuration settings
    """
    DB_HOST : str = os.environ.get("DB_HOST")
    DB_USER : str = os.environ.get("DB_USER")
    DB_NAME : str = os.environ.get("DB_NAME")
    DB_PASS : str = os.environ.get("DB_PASS")
    SECRET_KEY :str = os.environ.get("SECRET_KEY")
    ALGORITHM : str = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES : int = os.environ.get("ALGORITHM")

settings = Settings()