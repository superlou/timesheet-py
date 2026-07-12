import bcrypt
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from tortoise.contrib.fastapi import register_tortoise

from . import auth
from .models import User
from .routes import install

register_tortoise(
    app,
    db_url="sqlite://./data/db.sqlite3",
    modules={"models": ["timesheet_py.models"]},
)


app.include_router(install.router)


@ui.page("/")
def index():
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to("/login")

    with ui.column().classes("absolute-center items-center"):
        ui.label(f"Hello {app.storage.user['username']}!").classes("text-2xl")
        ui.button(on_click=logout, icon="logout").props("outline round")


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


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
