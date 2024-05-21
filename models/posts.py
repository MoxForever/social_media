import datetime
import time
from dataclasses import dataclass

from fastapi import UploadFile

from models.users import User
from utils import connection


@dataclass
class Post:
    id: int
    user: User
    text: str
    date: datetime.datetime
    likes: int
    img_url: str

    @staticmethod
    def create(user: User, text: str, image: UploadFile):
        if image.size > 0:
            extension = image.filename.split(".")[-1]
            filename = f"{time.time():.0f}.{extension}"
            with open(f"media/files/{filename}", "wb") as f:
                f.write(image.file.read())
            file_url = f"/media/files/{filename}"
        else:
            file_url = None

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, text, img_url) VALUES (%s, %s, %s) RETURNING *",
            (user.id, text, file_url)
        )
        post = Post._db_to_model(cursor.fetchone())
        cursor.close()
        connection.commit()
        return post

    @staticmethod
    def _db_to_model(data: list, user: User = None):
        if user is None:
            user = User.get_by_id(data[1])
        return Post(
            id=data[0],
            user=user,
            text=data[2],
            date=data[3],
            likes=data[4],
            img_url=data[5]
        )

    @staticmethod
    def get_by_id(post_id: int):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        posts = Post._db_to_model(cursor.fetchone())
        cursor.close()
        return posts

    @staticmethod
    def get_all_by_user(user: User):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY date DESC", (user.id,))
        posts = []
        for i in cursor.fetchall():
            posts.append(Post._db_to_model(i, user))
        cursor.close()
        return posts
