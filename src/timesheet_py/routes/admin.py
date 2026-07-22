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


class ProjectRow:
    def __init__(self, project: Project, editing: bool = False):
        self.project = project
        self.editing = editing

    @ui.refreshable_method
    def display(self):
        if self.editing:
            with ui.item_section():
                code_input = ui.input(value=self.project.code).props("dense")
            with ui.item_section():
                name_input = ui.input(value=self.project.name).props("dense")
            with ui.item_section():
                open_input = ui.checkbox(value=self.project.open).props("dense")
            with ui.item_section():
                ui.button(
                    icon="save",
                    on_click=lambda: self.save(
                        code_input.value, name_input.value, open_input.value
                    ),
                )
        else:
            with ui.item_section():
                ui.label(self.project.code)

            with ui.item_section():
                ui.label(self.project.name)

            with ui.item_section():
                ui.label("open" if self.project.open else "closed")

            with ui.item_section():
                ui.button(icon="edit", on_click=self.edit).props("flat dense")

    def edit(self):
        self.editing = True
        self.display.refresh()

    async def save(self, code: str, name: str, open: bool):
        self.project.code = code
        self.project.name = name
        self.project.open = open
        await self.project.save()
        self.editing = False
        self.display.refresh()


@router.page("/projects")
async def projects(user: CurrentUser):
    header(user)

    @ui.refreshable
    async def projects_list():
        projects = await Project.all()
        with ui.list().props("bordered separator").classes("w-full"):
            ui.item_label("Projects").props("header").classes("text-bold")
            ui.separator()

            for project in projects:
                with ui.item():
                    ProjectRow(project).display()

            with ui.item():
                with ui.item_section():
                    new_project_code = ui.input("Code").props("dense")
                with ui.item_section():
                    new_project_name = ui.input("Name").props("dense")
                with ui.item_section():
                    new_project_open = ui.checkbox().props("dense")

                with ui.item_section():
                    ui.button(icon="add", on_click=lambda: create_project()).props(
                        "flat dense"
                    )

            async def create_project():
                await Project.create(
                    code=new_project_code.value,
                    name=new_project_name.value,
                    open=new_project_open.value,
                )
                new_project_code.value = ""
                new_project_name.value = ""
                projects_list.refresh()

    await projects_list()


class ActivityRow:
    def __init__(self, activity: Activity, editing: bool = False):
        self.activity = activity
        self.editing = editing

    @ui.refreshable_method
    def display(self):
        if self.editing:
            with ui.item_section():
                code_input = ui.input(value=self.activity.code).props("dense")
            with ui.item_section():
                name_input = ui.input(value=self.activity.name).props("dense")
            # with ui.item_section():
            #     open_input = ui.checkbox(value=self.activity.open).props("dense")
            with ui.item_section():
                ui.button(
                    icon="save",
                    on_click=lambda: self.save(
                        code_input.value,
                        name_input.value,  # , open_input.value
                    ),
                )
        else:
            with ui.item_section():
                ui.label(self.activity.code)

            with ui.item_section():
                ui.label(self.activity.name)

            # with ui.item_section():
            #     ui.label("open" if self.activity.open else "closed")

            with ui.item_section():
                ui.button(icon="edit", on_click=self.edit).props("flat dense")

    def edit(self):
        self.editing = True
        self.display.refresh()

    async def save(self, code: str, name: str):  # , open: bool):
        self.activity.code = code
        self.activity.name = name
        self.activity.open = open
        await self.activity.save()
        self.editing = False
        self.display.refresh()


@router.page("/activities")
async def activities(user: CurrentUser):
    header(user)

    @ui.refreshable
    async def activities_list():
        activities = await Activity.all()
        with ui.list().props("bordered separator").classes("w-full"):
            ui.item_label("Activities").props("header").classes("text-bold")
            ui.separator()

            for activity in activities:
                with ui.item():
                    ActivityRow(activity).display()

            with ui.item():
                with ui.item_section():
                    new_activity_code = ui.input("Code")

                with ui.item_section():
                    new_activity_name = ui.input("Name")

                with ui.item_section():
                    ui.button(icon="add", on_click=lambda: create_activity()).props(
                        "flat dense"
                    )

        async def create_activity():
            await Activity.create(
                code=new_activity_code.value, name=new_activity_name.value
            )
            new_activity_code.value = ""
            new_activity_name.value = ""
            activities_list.refresh()

    await activities_list()


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
