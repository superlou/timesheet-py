from nicegui import app, ui
from nicegui.ui import navigate
from tortoise.contrib.fastapi import register_tortoise

from timesheet_py.models import User

from . import auth  # noqa: F401
from .components.header import header
from .routes import install
from .routes import user as user_route

register_tortoise(
    app,
    db_url="sqlite://./data/db.sqlite3",
    modules={"models": ["timesheet_py.models"]},
)


app.include_router(install.router)


@ui.page("/")
async def index():
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to("/login")

    user = await User.filter(email=app.storage.user["email"]).first()
    if user is None:
        ui.navigate.to("/login")
        return

    header(user)

    pass


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
