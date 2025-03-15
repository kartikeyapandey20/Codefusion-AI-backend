from fastapi import APIRouter
from api.v1.auth.route import AuthenticationRouter
from api.v1.users.route import UserRouter
from api.v1.news.router import router as news_router
api_router = APIRouter()

api_router.include_router(AuthenticationRouter().router)
api_router.include_router(UserRouter().router)
api_router.include_router(news_router)

@api_router.get("/")
def index():
	return {"status": "ok"}
