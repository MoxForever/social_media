from typing import Annotated

from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse

from models import User, HttpError
from utils import templates

login_route = APIRouter()


@login_route.get("/login")
async def login_page(request: Request):
    if request.scope["user"] is not None:
        return RedirectResponse(url="/profile", status_code=302)
    return templates.TemplateResponse(request, "login.html")


@login_route.post("/login")
async def login(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
):
    user = User.get_by_username(username)

    if user is None:
        raise HttpError("Пользователь не найден")

    if not user.password_check(password):
        raise HttpError("Пароль неверный")

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("user_id", str(user.id), expires=3600*24*30)
    return response
