from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.models import User


async def users(user: CurrentUser):
    ui.page_title("Admin - Users")

    async def update_user_admin(user, value):
        user.admin = value
        await user.save()

    async def update_user_api_access(user, value):
        user.api_access = value
        await user.save()

    async def update_user_approvers(user, approvers):
        await user.approvers.clear()
        await user.approvers.add(*approvers)

    async def delete_user(user: User):
        await user.delete()
        user_table.refresh()

    dialog = ui.dialog()

    def open_delete_user_dialog(user: User):
        dialog.clear()
        with dialog, ui.card():
            with ui.card_section():
                ui.label(f"Delete {user.name}?").classes("text-h6")

            with ui.card_section():
                ui.label(
                    f"This will delete all data associated with the user {user.email}."
                )

            with ui.card_section():
                with ui.row():
                    ui.button("Cancel", on_click=dialog.close)
                    ui.button("Delete", on_click=lambda: delete_user(user))

        dialog.open()

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
                with ui.item_section():
                    pass

            for user in users:
                with ui.item():
                    with ui.item_section():
                        ui.label(user.full_name)
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
                    with ui.item_section():
                        ui.button(
                            icon="delete",
                            on_click=lambda user=user: open_delete_user_dialog(user),
                        ).props("flat")

    ui.label("Users")
    await user_table()
