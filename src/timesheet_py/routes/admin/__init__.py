from fastapi import Depends, HTTPException, status
from nicegui import APIRouter, ui
from tortoise.transactions import in_transaction

from timesheet_py.auth import CurrentUser
from timesheet_py.components.admin_menu import admin_menu
from timesheet_py.components.header import header
from timesheet_py.models import Timesheet, TimesheetSet, User

from .activities import activities
from .projects import projects
from .timesheet_sets import timesheet_sets, timesheet_sets_edit, timesheets_sets_new
from .users import users


async def user_is_admin(user: CurrentUser):
    if not user.admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN)


router = APIRouter(prefix="/admin", dependencies=[Depends(user_is_admin)])
router.page("/projects")(projects)
router.page("/activities")(activities)
router.page("/users")(users)
router.page("/timesheet_sets")(timesheet_sets)
router.page("/timesheet_sets/new")(timesheets_sets_new)
router.page("/timesheet_sets/{timesheet_set_id}")(timesheet_sets_edit)


@router.page("/")
async def admin(user: CurrentUser):
    header(user)
    admin_menu()
