from nicegui import app, ui

from timesheet_py.components.header import header
from timesheet_py.models import User


@ui.page("/user")
async def user():
    async def update_user():
        await user.save()

    user = await User.filter(email=app.storage.user["email"]).first()
    if user is None:
        ui.navigate.to("/login")
        return

    header(user)

    name = ui.input("Name").bind_value(user, "name")
    email = ui.input("Email").bind_value(user, "email")
    employee_id = ui.input("Employee ID").bind_value(user, "employee_id")
    ui.label(f"Admin: {user.admin}")
    ui.button("Save", on_click=update_user)
