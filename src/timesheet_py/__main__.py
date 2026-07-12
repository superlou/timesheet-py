from nicegui import app, ui
from tortoise.contrib.fastapi import register_tortoise

from .routes import install
from . import auth  # noqa: F401

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


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
