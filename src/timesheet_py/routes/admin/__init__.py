from fastapi import Depends, HTTPException, status
from nicegui import APIRouter, ui
from tortoise.transactions import in_transaction

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import Timesheet, TimesheetSet, User

from .activities import activities
from .projects import projects
from .users import users


async def user_is_admin(user: CurrentUser):
    if not user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


router = APIRouter(prefix="/admin", dependencies=[Depends(user_is_admin)])
router.page("/projects")(projects)
router.page("/activities")(activities)
router.page("/users")(users)


@router.page("/")
async def admin(user: CurrentUser):
    header(user)
    ui.label("Admin")
    ui.link("Timesheet Sets", timesheet_sets)
    ui.link("Projects", projects)
    ui.link("Activities", activities)
    ui.link("Users", users)


@router.page("/timesheet_sets")
async def timesheet_sets(user: CurrentUser):
    header(user)
    ui.label("Timesheet Sets")
    ui.link("New", timesheets_new)

    with ui.list():
        for timesheet_set in await TimesheetSet.all().prefetch_related("submitters"):
            num_submitters = len(timesheet_set.submitters)
            ui.label(
                f"{timesheet_set.start} - {timesheet_set.finish} ({num_submitters} submitters, {'open' if timesheet_set.open else 'closed'})"
            )


@router.page("/timesheets/new")
async def timesheets_new(user: CurrentUser):
    async def create_timesheet_set():
        start, finish = date_range.value.split(" - ")
        timesheet_set = TimesheetSet(start=start, finish=finish, open=True)

        async with in_transaction() as conn:
            await timesheet_set.save()

            for user, checkbox in submitters.items():
                if checkbox.value:
                    await Timesheet.create(
                        timesheet_set=timesheet_set,
                        user=user,
                    )

        ui.navigate.to(timesheet_sets)

    header(user)

    ui.label("New Timesheet")

    with ui.row():
        with ui.column():
            ui.label("Dates")
            date_range = ui.date_input("Range", range_input=True)
            ui.button("Create timesheet", on_click=create_timesheet_set)

        with ui.column():
            ui.label("Submitters")
            submitters = {
                user: ui.checkbox(f"{user.name} ({user.email})", value=True)
                for user in await User.all()
            }
