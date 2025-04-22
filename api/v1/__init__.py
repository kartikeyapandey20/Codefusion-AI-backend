from fastapi import APIRouter
from api.v1.auth.route import AuthenticationRouter
from api.v1.users.route import UserRouter
from api.v1.news.router import NewsRouter
from api.v1.question.router import QuestionRouter
from api.v1.chat.route import ChatRouter
from api.v1.discuss.router import DiscussRouter
api_router = APIRouter()

api_router.include_router(AuthenticationRouter().router)
api_router.include_router(UserRouter().router)
api_router.include_router(NewsRouter().router)
api_router.include_router(QuestionRouter().router)
api_router.include_router(ChatRouter().router)
api_router.include_router(DiscussRouter().router)

@api_router.get("/")
def index():
	return {"status": "ok"}
