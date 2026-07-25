from fastapi import HTTPException, status
from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.admin_menu import AdminMenu

from .activities import activities
from .projects import projects
from .timesheet_sets import timesheet_sets, timesheet_sets_edit, timesheet_sets_new
from .users import users


async def admin(user: CurrentUser):
    if not user.admin:
        ui.label("Forbidden")
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    with ui.row().classes("w-full"):
        with ui.column().classes("col-2"):
            AdminMenu().display()
        with ui.column().classes("col-9"):
            ui.sub_pages(
                {
                    "/": admin_index,
                    "/timesheet_sets": lambda: timesheet_sets(user),
                    "/timesheet_sets/new": lambda: timesheet_sets_new(user),
                    "/timesheet_sets/{timesheet_set_id}": lambda timesheet_set_id: timesheet_sets_edit(
                        timesheet_set_id, user
                    ),
                    "/users": lambda: users(user),
                    "/projects": projects,
                    "/activities": lambda: activities(user),
                }
            ).classes("w-full")


async def admin_index():
    ui.label("Admin")
    ui.label("These settings configure the Timesheet Entry application.")
