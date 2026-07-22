from typing import Annotated

from fastapi import Depends, Request
from nicegui import app, html, ui
from tortoise.contrib.fastapi import register_tortoise

from timesheet_py.auth import CurrentUser
from timesheet_py.models import Timesheet, TimesheetSet, User

from . import (
    auth,  # noqa: F401
    routes,
)
from .components.header import header

register_tortoise(
    app,
    db_url="sqlite://./data/db.sqlite3",
    modules={"models": ["timesheet_py.models"]},
)

app.include_router(routes.install.router)
app.include_router(routes.admin.router)
app.include_router(routes.timesheet.router)


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
            color = "positive"
        elif timesheet.submitted:
            value = 0.5
            color = "primary"
        else:
            value = 0
            color = "warning"

        ui.circular_progress(value, color=color, show_value=False, size="1.4em").props(
            "thickness=0.5"
        )

    def timesheet_link(timesheet: Timesheet):
        if current_user == timesheet.user:
            ui.link(
                timesheet.user.name,
                str(request.url_for("timesheet", timesheet_id=timesheet.id)),
            )
        elif current_user in timesheet.user.approvers and timesheet.submitted:
            with ui.row():
                ui.label(timesheet.user.name)
                ui.link(
                    "approve",
                    str(request.url_for("timesheet", timesheet_id=timesheet.id)),
                )
        else:
            ui.label(timesheet.user.name)

    def timesheet_status_row(timesheet: Timesheet):
        timesheet_status(timesheet)
        timesheet_link(timesheet)

    for timesheet_set in open_timesheet_sets:
        timesheets = timesheet_set.timesheets
        submitted_fraction = sum(t.submitted for t in timesheets) / len(timesheets)
        approved_fraction = sum(t.approved for t in timesheets) / len(timesheets)
        header_text = f"{timesheet_set.start.strftime('%m/%d/%Y')} to {timesheet_set.finish.strftime('%m/%d/%Y')}"

        with (
            ui.expansion(value=True)
            .props("bordered")
            .classes("w-full items-center") as expansion
        ):
            with expansion.add_slot("header"):
                with ui.row().classes("w-full items-center"):
                    ui.label(header_text)
                    with ui.column().classes("w-50 gap-1"):
                        ui.linear_progress(value=submitted_fraction, show_value=False)
                        ui.linear_progress(
                            value=approved_fraction, show_value=False, color="green"
                        )

            with ui.grid(columns="1em auto").classes("items-center"):
                for timesheet in timesheet_set.timesheets:
                    timesheet_status_row(timesheet)


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret)
