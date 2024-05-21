from typing import Annotated

from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse

from models import User, HttpError
from utils import templates

register_route = APIRouter()


@register_route.get("/register")
async def register_page(request: Request):
    if request.scope["user"] is not None:
        return RedirectResponse(url="/profile", status_code=302)
    return templates.TemplateResponse(request, "register.html")


@register_route.post("/register")
async def register(
        username: Annotated[str, Form()],
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        password_confirm: Annotated[str, Form()]
):
    if password != password_confirm:
        raise HttpError("Пароли должны совпадать")

    user = User(
        email=email,
        username=username
    )
    user.set_password(password)
    user.save()

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("user_id", str(user.id), expires=3600*24*30)
    return response
