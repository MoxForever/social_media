from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from models import User


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        user_id = request.cookies.get("user_id", None)
        if user_id is not None:
            user = User.get_by_id(int(user_id))
        else:
            user = None

        request.scope["user"] = user
        return await call_next(request)
