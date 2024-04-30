import hashlib
from typing import Annotated

import psycopg2
from fastapi import FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

connection = psycopg2.connect("postgres://postgres:123456@localhost:5432/social_media")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates("templates")


@app.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.post("/register")
async def register(
        username: Annotated[str, Form()],
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        password_confirm: Annotated[str, Form()]
):
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Пароли должны совпадать")
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
        (username, email, password_hashed)
    )
    user_id = cursor.fetchone()[0]
    cursor.close()
    connection.commit()

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("user_id", str(user_id), expires=3600*24*30)
    return response


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@app.post("/login")
async def login(
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
):
    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    cursor.close()

    if user_data is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    else:
        user_id = user_data[0]
        password_hashed_db = user_data[3]

    if password_hashed != password_hashed_db:
        raise HTTPException(status_code=400, detail="Пароль неверный")

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("user_id", str(user_id), expires=3600*24*30)
    return response


@app.get("/profile")
async def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html")