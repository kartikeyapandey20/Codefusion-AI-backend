from jose import JWTError, jwt
from datetime import datetime, timedelta
from .schema import TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.deps import get_db
from api.v1.users.model import User
from core.config import settings

# Initializing OAuth2PasswordBearer instance
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Retrieving settings values
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Function to create access token
def create_access_token(data: dict):
    """
    Create an access token.

    Args:
        data (dict): The data to be encoded in the token.

    Returns:
        str: The encoded access token.
    """
    to_encode = data.copy()  # Copying the input data
    
    # Calculating token expiry time
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})  # Updating the token with expiry time

    # Encoding the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Function to verify access token
def verify_access_token(token: str, credentials_exception):
    """
    Verify the access token.

    Args:
        token (str): The access token string.
        credentials_exception (HTTPException): The exception to raise if credentials are invalid.

    Raises:
        HTTPException: If the token cannot be decoded.
        credentials_exception: If the user ID is not found in the token payload.

    Returns:
        TokenData: An instance of TokenData containing the user ID.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)  # Decoding the token

        id: str = payload.get("user_id")  # Extracting user ID from the payload
        
        if id is None:
            raise credentials_exception  # If user ID is not found, raise an exception
        
        token_data = TokenData(id=id)  # Creating TokenData object
    except JWTError:
        raise credentials_exception  # If JWTError occurs, raise an exception
    
    return token_data

# Function to get current user using access token
def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)):
    """
    Get the current user using the access token.

    Args:
        token (str): The access token string.
        db (Session): The SQLAlchemy database session.

    Returns:
        User: The current user.
    """
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate the credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token = verify_access_token(token, credential_exception)  # Verifying access token
    user = db.query(User).filter(User.id == token.id).first()  # Retrieving user from database
    
    return user
