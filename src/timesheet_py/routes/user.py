from nicegui import app, ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import User


@ui.page("/user")
async def user(user: CurrentUser):
    async def update_user():
        await user.save()

    header(user)

    name = ui.input("Name").bind_value(user, "name")
    email = ui.input("Email").bind_value(user, "email")
    code = ui.input("Employee ID").bind_value(user, "code")
    ui.label(f"Admin: {user.admin}")
    ui.button("Save", on_click=update_user)
