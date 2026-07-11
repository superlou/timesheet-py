from starlette.authentication import AuthenticationBackend
from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import ui, app

from starlette.middleware.base import BaseHTTPMiddleware

unrestricted_page_routes = {"/login"}

passwords = {"admin": "admin"}

@app.add_middleware
class AuthMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if app.storage.user.get("authenticated") or path in unrestricted_page_routes or path.startswith("/_nicegui"):
            return await call_next(request)

        return RedirectResponse(f"/login?redirect_to={path}")

@ui.page("/")
def index():
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to("/login")

    with ui.column().classes("absolute-center items-center"):
        ui.label(f"Hello {app.storage.user["username"]}!").classes('text-2xl')
        ui.button(on_click=logout, icon='logout').props("outline round")

@ui.page("/login")
def login(redirect_to: str = "/") -> RedirectResponse | None:
    if app.storage.user.get("authenticated"):
        return RedirectResponse(redirect_to)

    def try_login() -> None:
        if passwords.get("admin") == password.value:
            app.storage.user.update(username=username.value, authenticated=True)
            ui.navigate.to(redirect_to)
        else:
            ui.notify("Wrong username or password", color="negative")

    with ui.card().classes("absolute-center items-stretch"):
        username = ui.input("Username").props("autofocus").on("keydown.enter", lambda: password.run_method("focus"))
        password = ui.input("Password", password=True, password_toggle_button=True).on("keydown.enter", try_login)
        ui.button("Log in", on_click=try_login)

    return None

ui.run(storage_secret="nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c=")
