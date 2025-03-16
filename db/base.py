# This file is for alembic

# Import all the models, so that Base has them before being
# imported by Alembic

from .database import Base
import api.v1.question.model  
import api.v1.users.model
import api.v1.chat.model
import api.v1.news.model

