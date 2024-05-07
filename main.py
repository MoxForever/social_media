import hashlib
import time
from typing import Annotated

import psycopg2
from fastapi import FastAPI, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

connection = psycopg2.connect("postgres://postgres:123456@localhost:5432/social_media")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"))
app.mount("/media", StaticFiles(directory="media"))
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
    cursor = connection.cursor()
    user_id = int(request.cookies["user_id"])
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY date DESC", (user_id,))
    posts = [{"text": i[2], "date": i[3], "img_url": i[5]} for i in cursor.fetchall()]
    cursor.close()
    return templates.TemplateResponse(
        request, "profile.html", {
            "name": user_data[2],
            "about": user_data[4],
            "avatar_url": user_data[5],
            "posts": posts,
        }
    )


@app.post("/profile")
async def profile(request: Request, text: Annotated[str, Form()], file: UploadFile):
    user_id = int(request.cookies["user_id"])
    if file:
        extension = file.filename.split(".")[-1]
        filename = f"{time.time():.0f}.{extension}"
        with open(f"media/files/{filename}", "wb") as f:
            f.write(file.file.read())
        file_url = f"/media/files/{filename}"
    else:
        file_url = None
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO posts (user_id, text, img_url) VALUES (%s, %s, %s)",
        (user_id, text, file_url)
    )
    cursor.close()
    connection.commit()

    return RedirectResponse("/profile", status_code=302)


@app.get("/settings")
async def settings_page(request: Request):
    cursor = connection.cursor()
    user_id = int(request.cookies["user_id"])
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()

    return templates.TemplateResponse(
        request, "settings.html", {
            "nickname": user_data[2],
            "email": user_data[1],
            "about": user_data[4] or ""
        }
    )


@app.post("/settings/profile")
async def settings(
        request: Request,
        nickname: Annotated[str, Form()],
        email: Annotated[str, Form()],
        avatar: UploadFile | None,
        about: Annotated[str, Form()]
):
    user_id = int(request.cookies["user_id"])
    if avatar:
        extension = avatar.filename.split(".")[-1]
        with open(f"media/avatars/{user_id}.{extension}", "wb") as f:
            f.write(avatar.file.read())
        avatar_url = f"/media/avatars/{user_id}.{extension}"
    else:
        avatar_url = None

    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET username = %s, email = %s, about = %s WHERE id = %s",
        (nickname, email, about, user_id),
    )
    if avatar_url:
        cursor.execute("UPDATE users SET avatar_url = %s WHERE id = %s", (avatar_url, user_id))
    connection.commit()

    return RedirectResponse(status_code=302, url="/profile")


@app.post("/settings/password")
async def settings(
        request: Request,
        password: Annotated[str, Form()],
        password_confirm: Annotated[str, Form()],
):
    if password != password_confirm:
        raise HTTPException(status_code=400, detail="Пароли должны совпадать")

    password_hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user_id = int(request.cookies["user_id"])
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (password_hashed, user_id),
    )
    connection.commit()

    return RedirectResponse(status_code=302, url="/profile")
