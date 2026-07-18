from fastapi import Depends, HTTPException, status
from nicegui import APIRouter, ui
from tortoise.transactions import in_transaction

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import Activity, Project, Timesheet, TimesheetSet, User


async def user_is_admin(user: CurrentUser):
    if not user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


router = APIRouter(prefix="/admin", dependencies=[Depends(user_is_admin)])


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


@router.page("/projects")
async def projects(user: CurrentUser):
    header(user)
    ui.label("Projects")

    @ui.refreshable
    async def projects_list():
        projects = await Project.all()
        with ui.grid(columns=3):
            ui.label("Code")
            ui.label("Name")
            ui.label("Open")

            for project in projects:
                ui.label(project.code)
                ui.label(project.name)
                ui.label(str(project.open))

    async def create_project():
        await Project.create(code=new_project_code.value, name=new_project_name.value)
        new_project_code.value = ""
        new_project_name.value = ""
        projects_list.refresh()

    await projects_list()

    with ui.row().classes("items-center"):
        ui.label("New project")
        new_project_code = ui.input("Code")
        new_project_name = ui.input("Name")
        ui.button("Create", on_click=create_project)


@router.page("/activities")
async def activities(user: CurrentUser):
    header(user)
    ui.label("Activities")

    @ui.refreshable
    async def activities_list():
        activities = await Activity.all()
        with ui.grid(columns=2):
            ui.label("Code")
            ui.label("Name")

            for activity in activities:
                ui.label(activity.code)
                ui.label(activity.name)

    async def create_activity():
        await Activity.create(
            code=new_activity_code.value, name=new_activity_name.value
        )
        new_activity_code.value = ""
        new_activity_name.value = ""
        activities_list.refresh()

    await activities_list()

    with ui.row().classes("items-center"):
        ui.label("New activity")
        new_activity_code = ui.input("Code")
        new_activity_name = ui.input("Name")
        ui.button("Create", on_click=create_activity)


@router.page("/users")
async def users(user: CurrentUser):
    header(user)
    ui.label("Users")

    async def update_user_admin(user, value):
        user.admin = value
        await user.save()

    async def update_user_approvers(user, approvers):
        await user.approvers.clear()
        await user.approvers.add(*approvers)

    @ui.refreshable
    async def user_table():
        users = await User.all().prefetch_related("approvers")

        with ui.grid(columns=4).classes("items-center"):
            ui.label("Name")
            ui.label("Email")
            ui.label("Admin")
            ui.label("Approver")

            for user in users:
                ui.label(user.name)
                ui.label(user.email)
                ui.checkbox(
                    value=user.admin,
                    on_change=lambda evt, user=user: update_user_admin(user, evt.value),
                )
                ui.select(
                    {user: user.name for user in users},
                    value=[approver for approver in user.approvers],
                    multiple=True,
                    on_change=lambda evt, user=user: update_user_approvers(
                        user, evt.value
                    ),
                )

    await user_table()
