# This file is for alembic

# Import all the models, so that Base has them before being
# imported by Alembic

from .database import Base
from api.v1.users.model import User
from api.v1.category.model import Category
from api.v1.project.model import Project
from api.v1.chat.model import UserResponse , AiResponse , Chat



