from db.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, ARRAY

class Project(Base):

    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, nullable=False)
    project_name = Column(String, nullable=False)
    document_url = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    category_id = Column(Integer , ForeignKey("category.id", ondelete="CASCADE"),nullable=False)
