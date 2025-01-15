from passlib.context import CryptContext

# Initialize a CryptContext object with bcrypt hashing scheme
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str):
    """Hashes a password using bcrypt.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Verifies a plaintext password against a hashed password.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
