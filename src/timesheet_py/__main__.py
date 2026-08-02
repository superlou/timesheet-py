from fastapi import Request
from nicegui import app, ui
from tortoise.contrib.fastapi import register_tortoise

from timesheet_py.auth import CurrentUser
from timesheet_py.models import Timesheet, TimesheetSet, User
from timesheet_py.routes.admin import admin
from timesheet_py.routes.user import edit_user_profile

from . import (
    api,
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
app.include_router(api.router)


async def open_timesheet_sets() -> list[TimesheetSet]:
    return await TimesheetSet.filter(open=True).prefetch_related(
        "timesheets", "timesheets__user", "timesheets__user__approvers"
    )


async def open_timesheets_list(current_user: User, request: Request):
    open_timesheet_sets = await TimesheetSet.filter(open=True).prefetch_related(
        "timesheets", "timesheets__user", "timesheets__user__approvers"
    )

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
                timesheet.user.full_name,
                f"/timesheet/{timesheet.id}",
            )
        elif current_user in timesheet.user.approvers and timesheet.submitted:
            with ui.row():
                ui.label(timesheet.user.full_name)
                ui.link("approve", f"/timesheet/{timesheet.id}")
        else:
            ui.label(timesheet.user.full_name)

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


def set_title(path: str):
    # Set title if nothing else sets it
    ui.page_title("Timesheet Entry")


@ui.page("/")
@ui.page("/timesheet/{timesheet_id}")
@ui.page("/user")
@ui.page("/admin")
@ui.page("/admin/{_:path}")
async def index(
    current_user: CurrentUser,
    request: Request,
):
    ui.page_title("Timesheet Entry")
    header(current_user)

    ui.sub_pages(
        {
            "/": lambda: open_timesheets_list(current_user, request),
            "/timesheet/{timesheet_id}": lambda timesheet_id: routes.timesheet.timesheet(
                timesheet_id,
                current_user,
            ),
            "/user": lambda: edit_user_profile(current_user),
            "/admin": lambda: admin(current_user),
        }
    ).classes("w-full")

    ui.context.client.sub_pages_router.on_path_changed(set_title)


secret = "nB1NgSC1EbOtojVIpZ2TGBhpUTs1h6R1U4jFpfJXA+c="
ui.run(storage_secret=secret, fastapi_docs=True)
