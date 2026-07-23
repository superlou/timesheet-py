import secrets

from nicegui import app, ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import APIKey, User


@ui.page("/user")
async def user(user: CurrentUser):
    async def update_user():
        await user.save()

    async def delete_key(key: APIKey):
        await key.delete()
        list_keys.refresh()

    async def create_key():
        await APIKey.create(user=user, key=secrets.token_urlsafe(32))
        list_keys.refresh()

    @ui.refreshable
    async def list_keys():
        with ui.list().props("bordered separator").classes("w-full"):
            ui.item_label("API Keys").props("header").classes("text-bold")
            ui.separator()

            keys = await APIKey.filter(user=user).all()

            if len(keys) > 0:
                for key in keys:
                    with ui.item():
                        with ui.item_section().classes("col-11"):
                            ui.label(str(key.key))

                        with ui.item_section().classes("col-1"):
                            ui.button(
                                icon="delete", on_click=lambda key=key: delete_key(key)
                            ).props("flat")
            else:
                with ui.item():
                    with ui.item_section():
                        ui.label("(none)")

            with ui.item():
                ui.button(icon="add", on_click=create_key)

    header(user)

    ui.input("Name").bind_value(user, "name")
    ui.input("Email").bind_value(user, "email")
    ui.input("Employee ID").bind_value(user, "code")
    ui.label(f"Admin: {user.admin}")
    ui.button("Save", on_click=update_user)

    if user.api_access:
        ui.separator()
        await list_keys()
