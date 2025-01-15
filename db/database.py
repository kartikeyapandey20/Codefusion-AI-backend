from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Extract database connection details from settings
DB_HOST = settings.DB_HOST
DB_USER = settings.DB_USER
DB_NAME = settings.DB_NAME
DB_PASS = settings.DB_PASS

# Construct the SQLAlchemy database URL
SQLALCHEMY_DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker to generate database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()
