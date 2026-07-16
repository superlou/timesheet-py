from typing import Annotated

from fastapi import Depends, Request
from nicegui import app, ui
from tortoise.contrib.fastapi import register_tortoise

from timesheet_py.auth import CurrentUser
from timesheet_py.models import TimesheetSet, User

from . import auth  # noqa: F401
from .components.header import header
from .routes import admin as admin_route
from .routes import install as install_route
from .routes import timesheet as timesheet_route
from .routes import user as user_route

register_tortoise(
    app,
    db_url="sqlite://./data/db.sqlite3",
    modules={"models": ["timesheet_py.models"]},
)

app.include_router(install_route.router)
app.include_router(admin_route.router)
app.include_router(timesheet_route.router)


async def open_timesheet_sets() -> list[TimesheetSet]:
    return await TimesheetSet.filter(open=True).prefetch_related("submitters")


OpenTimesheetSets = Annotated[list[TimesheetSet], Depends(open_timesheet_sets)]


@ui.page("/")
async def index(
    current_user: CurrentUser,
    open_timesheet_sets: OpenTimesheetSets,
    request: Request,
):
    def logout() -> None:
        app.storage.user.clear()
        ui.navigate.to("/login")

    header(current_user)

    for timesheet_set in open_timesheet_sets:
        ui.label(f"{timesheet_set.start} through {timesheet_set.start}")
        with ui.list().props("dense separator"):
            for user in timesheet_set.submitters:
                if current_user == user:
                    with ui.item():
                        ui.link(
                            user.name,
                            str(
                                request.url_for(
                                    "timesheet_for_current_user",
                                    timesheet_set_id=timesheet_set.id,
                                )
                            ),
                        )
                else:
                    ui.item(user.name)


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
