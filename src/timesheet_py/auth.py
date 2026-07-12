import bcrypt
from fastapi import Request
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from starlette.middleware.base import BaseHTTPMiddleware

from .models import User

unauthenticated_page_routes = {
    "/login",
    "/install",
    "/install/",
    "/users/new",
}


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


@ui.page("/login")
async def login(redirect_to: str = "/") -> RedirectResponse | None:
    if app.storage.user.get("authenticated"):
        return RedirectResponse(redirect_to)

    async def try_login() -> None:
        user = await User.filter(email=email.value).first()

        if user and bcrypt.checkpw(
            password.value.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            app.storage.user.update(
                username=email.value,
                authenticated=True,
                admin=user.admin,
            )
            ui.navigate.to(redirect_to)
        else:
            ui.notify("Wrong username or password", color="negative")

    with ui.card().classes("absolute-center items-stretch"):
        email = (
            ui.input("Email")
            .props("autofocus")
            .on("keydown.enter", lambda: password.run_method("focus"))
        )
        password = ui.input("Password", password=True, password_toggle_button=True).on(
            "keydown.enter", try_login
        )
        ui.button("Log in", on_click=try_login)
        ui.link("Create account", "/users/new")

    return None


@ui.page("/users/new")
def new_user():
    async def create_user() -> None:
        password_hash = bcrypt.hashpw(
            password.value.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        await User.create(
            email=email.value,
            name=name.value,
            employee_id=employee_id.value,
            password_hash=password_hash,
        )
        ui.navigate.to("/login")

    with ui.card().classes("absolute-center items-stretch"):
        ui.label("Create account")
        email = ui.input("Email").props("autofocus")
        with ui.row():
            name = ui.input("Name")
            employee_id = ui.input("Employeed ID")

        password = ui.input("Password", password=True, password_toggle_button=True)

        ui.button("Create", on_click=create_user)
