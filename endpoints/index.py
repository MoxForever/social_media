from fastapi import Request, APIRouter
from fastapi.responses import RedirectResponse

from models import User
from utils import templates

index_router = APIRouter()


@index_router.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html", {"users": User.get_some_users()})
