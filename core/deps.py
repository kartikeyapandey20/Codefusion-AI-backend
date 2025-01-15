from db.database import SessionLocal

def get_db():
    """Provide a database session.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
