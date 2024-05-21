import time
from typing import Annotated

from fastapi import Request, Form, APIRouter, UploadFile
from fastapi.responses import RedirectResponse

from models import User, Post
from utils import templates

profile_route = APIRouter()


@profile_route.get("/profile")
async def profile_page(request: Request):
    if request.scope["user"] is None:
        return RedirectResponse(url="/", status_code=302)
    user: User = request.scope["user"]
    return templates.TemplateResponse(
        request, "profile.html", {
            "user": user,
            "posts": Post.get_all_by_user(user),
            "is_own_page": True
        }
    )


@profile_route.post("/profile")
async def profile(request: Request, text: Annotated[str, Form()], file: UploadFile):
    user: User = request.scope["user"]
    Post.create(user, text, file)
    return RedirectResponse("/profile", status_code=302)


@profile_route.get("/profile/{username}")
async def profile_user_page(request: Request, username: str):
    user = User.get_by_username(username)
    return templates.TemplateResponse(
        request, "profile.html", {
            "user": user,
            "posts": Post.get_all_by_user(user),
            "is_own_page": user.id == request.scope["user"].id
        }
    )

