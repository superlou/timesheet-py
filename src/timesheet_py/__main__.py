from typing import Annotated

from fastapi import Depends, Request
from nicegui import app, html, ui
from tortoise.contrib.fastapi import register_tortoise

from timesheet_py.auth import CurrentUser
from timesheet_py.models import Timesheet, TimesheetSet, User

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
    return await TimesheetSet.filter(open=True).prefetch_related(
        "timesheets", "timesheets__user", "timesheets__user__approvers"
    )


OpenTimesheetSets = Annotated[list[TimesheetSet], Depends(open_timesheet_sets)]


@ui.page("/")
async def index(
    current_user: CurrentUser,
    open_timesheet_sets: OpenTimesheetSets,
    request: Request,
):
    header(current_user)

    def timesheet_status(timesheet: Timesheet):
        if timesheet.approved:
            value = 1.0
            label = "Approved"
        elif timesheet.submitted:
            value = 0.5
            label = "Submitted"
        else:
            value = 0
            label = ""

        with ui.linear_progress(value, show_value=False, size="1.4em").classes("w-24"):
            with html.div().classes("absolute-full flex flex-center"):
                ui.label(label).classes("text-white text-caption")

    def timesheet_link(timesheet: Timesheet):
        if current_user == timesheet.user:
            ui.link(
                timesheet.user.name,
                str(request.url_for("timesheet", timesheet_id=timesheet.id)),
            )
        elif current_user in timesheet.user.approvers and timesheet.submitted:
            with html.span():
                ui.label(timesheet.user.name)
                ui.link(
                    "(approve)",
                    str(request.url_for("timesheet", timesheet_id=timesheet.id)),
                )
        else:
            ui.label(timesheet.user.name)

    def timesheet_status_row(timesheet: Timesheet):
        timesheet_link(timesheet)
        timesheet_status(timesheet)

    for timesheet_set in open_timesheet_sets:
        ui.label(f"{timesheet_set.start} through {timesheet_set.start}")
        with ui.grid(columns=2).classes("items-center"):
            for timesheet in timesheet_set.timesheets:
                timesheet_status_row(timesheet)


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
