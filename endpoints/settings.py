from typing import Annotated

from fastapi import Request, Form, APIRouter, UploadFile
from fastapi.responses import RedirectResponse

from models import User, HttpError
from utils import templates

settings_route = APIRouter()


@settings_route.get("/settings")
async def settings_page(request: Request):
    if request.scope["user"] is None:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        request, "settings.html", {"user": request.scope["user"]}
    )


@settings_route.post("/settings/profile")
async def settings(
        request: Request,
        username: Annotated[str, Form()],
        email: Annotated[str, Form()],
        avatar: UploadFile | None,
        about: Annotated[str, Form()]
):
    user: User = request.scope["user"]
    user.upload_avatar(avatar)
    user.username = username
    user.email = email
    user.about = about
    user.save()

    return RedirectResponse(status_code=302, url="/profile")


@settings_route.post("/settings/password")
async def settings(
        request: Request,
        password: Annotated[str, Form()],
        password_confirm: Annotated[str, Form()],
):
    if password != password_confirm:
        raise HttpError("Пароли должны совпадать")

    user: User = request.scope["user"]
    user.set_password(password)
    user.save()

    return RedirectResponse(status_code=302, url="/profile")
