from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.admin_menu import admin_menu
from timesheet_py.components.header import header
from timesheet_py.models import User


async def users(user: CurrentUser):
    header(user)

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

        with ui.list().props("bordered separator").classes("items-center w-full"):
            with ui.item():
                with ui.item_section():
                    ui.item_label("User").props("header").classes("text-bold")
                with ui.item_section():
                    ui.item_label("Admin").props("header").classes("text-bold")
                with ui.item_section():
                    ui.item_label("API Access").props("header").classes("text-bold")
                with ui.item_section():
                    ui.item_label("Approver").props("header").classes("text-bold")

            for user in users:
                with ui.item():
                    with ui.item_section():
                        ui.label(user.name)
                        ui.label(user.email).classes("text-caption")
                        ui.label(user.code).classes("text-caption")
                    with ui.item_section():
                        ui.checkbox(
                            value=user.admin,
                            on_change=lambda evt, user=user: update_user_admin(
                                user, evt.value
                            ),
                        )
                    with ui.item_section():
                        ui.checkbox(
                            value=user.api_access,
                            on_change=lambda evt, user=user: update_user_api_access(
                                user, evt.value
                            ),
                        )
                    with ui.item_section():
                        ui.select(
                            {user: user.name for user in users},
                            value=[approver for approver in user.approvers],
                            multiple=True,
                            on_change=lambda evt, user=user: update_user_approvers(
                                user, evt.value
                            ),
                        )

    with ui.row().classes("w-full"):
        with ui.column().classes("col-2"):
            admin_menu()
        with ui.column().classes("col-8"):
            ui.label("Users")
            await user_table()
