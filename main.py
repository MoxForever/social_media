from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware

from endpoints import settings_route, register_route, profile_route, login_route, index_router
from middlewares import UserMiddleware, ErrorMiddleware
from utils import templates

app = FastAPI(middleware=[Middleware(UserMiddleware), Middleware(ErrorMiddleware)])
app.mount("/static", StaticFiles(directory="static"))
app.mount("/media", StaticFiles(directory="media"))
app.include_router(settings_route)
app.include_router(register_route)
app.include_router(profile_route)
app.include_router(login_route)
app.include_router(index_router)


@app.exception_handler(RequestValidationError)
async def standard_validation_exception_handler(request: Request, _):
    return templates.TemplateResponse(request, "error.html", {"error": "Данные введены неверно"})
