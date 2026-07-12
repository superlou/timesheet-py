from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import app
from starlette.middleware.base import BaseHTTPMiddleware

unauthenticated_page_routes = {"/login", "/install", "/install/", "/users/new"}


@app.add_middleware
class AuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if (
            app.storage.user.get("authenticated")
            or path in unauthenticated_page_routes
            or path.startswith("/_nicegui")
        ):
            return await call_next(request)

        return RedirectResponse(f"/login?redirect_to={path}")
