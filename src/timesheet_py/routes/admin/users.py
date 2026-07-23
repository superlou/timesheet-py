from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import User


async def users(user: CurrentUser):
    header(user)
    ui.label("Users")

    async def update_user_admin(user, value):
        user.admin = value
        await user.save()

    async def update_user_api_access(user, value):
        user.api_access = value
        await user.save()

    async def update_user_approvers(user, approvers):
        await user.approvers.clear()
        await user.approvers.add(*approvers)

    @ui.refreshable
    async def user_table():
        users = await User.all().prefetch_related("approvers")

        with ui.grid(columns=6).classes("items-center"):
            ui.label("Name")
            ui.label("Email")
            ui.label("Code")
            ui.label("Admin")
            ui.label("API Access")
            ui.label("Approver")

            for user in users:
                ui.label(user.name)
                ui.label(user.email)
                ui.label(user.code)
                ui.checkbox(
                    value=user.admin,
                    on_change=lambda evt, user=user: update_user_admin(user, evt.value),
                )
                ui.checkbox(
                    value=user.api_access,
                    on_change=lambda evt, user=user: update_user_api_access(
                        user, evt.value
                    ),
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
