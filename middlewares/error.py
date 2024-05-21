from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from models import HttpError
from utils import templates


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await call_next(request)
        except HttpError as ex:
            return templates.TemplateResponse(request, "error.html", {"error": ex.error})
        except Exception:
            return templates.TemplateResponse(request, "error.html", {"error": "Неизвестная ошибка"})
