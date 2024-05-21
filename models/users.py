import hashlib
from dataclasses import dataclass

from fastapi import UploadFile

from utils import connection


@dataclass
class User:
    email: str
    username: str

    id: int | None = None
    about: str | None = None
    avatar_url: str | None = None
    password_hash: str | None = None

    def password_check(self, password: str):
        return self.password_hash == hashlib.sha256(password.encode("utf-8")).hexdigest()

    def set_password(self, password: str):
        self.password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    def upload_avatar(self, avatar: UploadFile):
        if avatar.size > 0:
            extension = avatar.filename.split(".")[-1]
            with open(f"media/avatars/{self.id}.{extension}", "wb") as f:
                f.write(avatar.file.read())
            self.avatar_url = f"/media/avatars/{self.id}.{extension}"
        else:
            self.avatar_url = None

    def save(self):
        cursor = connection.cursor()
        if self.id:
            cursor.execute(
                "UPDATE users SET username = %s, password_hash = %s, about = %s, avatar_url = %s WHERE id = %s RETURNING *",
                (self.username, self.password_hash, self.about, self.avatar_url, self.id))
        else:
            print(self)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, about, avatar_url) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                (self.username, self.email, self.password_hash, self.about, self.avatar_url)
            )

        user = User._db_to_model(cursor.fetchone())
        cursor.close()
        connection.commit()
        return user

    @staticmethod
    def get_by_id(user_id: int):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = User._db_to_model(cursor.fetchone())
        cursor.close()
        return user

    @staticmethod
    def get_by_username(username: str):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = User._db_to_model(cursor.fetchone())
        cursor.close()
        return user

    @staticmethod
    def get_some_users():
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users LIMIT 10")
        users = [User._db_to_model(i) for i in cursor.fetchall()]
        cursor.close()
        return users

    @staticmethod
    def _db_to_model(data: list | None):
        if data is None:
            return None

        return User(
            id=data[0],
            email=data[1],
            username=data[2],
            password_hash=data[3],
            about=data[4],
            avatar_url=data[5]
        )
