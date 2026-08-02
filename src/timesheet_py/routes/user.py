import secrets

from nicegui import app, ui

from timesheet_py.auth import CurrentUser, create_salted_hash
from timesheet_py.components.header import header
from timesheet_py.models import APIKey, Setting, User


async def edit_user_profile(user: CurrentUser):
    async def update_user():
        if new_password.value != "":
            user.password_hash = create_salted_hash(new_password.value)

        await user.save()
        new_password.value = ""
        ui.notify("Updated profile")

    async def delete_key(key: APIKey):
        await key.delete()
        list_keys.refresh()

    async def create_key():
        await APIKey.create(user=user, key=secrets.token_urlsafe(32))
        list_keys.refresh()

    ui.page_title("My Profile")

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

    if (await Setting.get(key="split_name")).value == "1":
        with ui.row():
            ui.input("First name").bind_value(user, "name")
            ui.input("Last name").bind_value(user, "last_name")
    else:
        ui.input("Name").bind_value(user, "name")
    ui.input("Email").bind_value(user, "email")
    ui.input("Employee ID").bind_value(user, "code")
    new_password = ui.input(
        f"New password", password=True, password_toggle_button=True
    ).props("autocomplete=new-password")
    ui.label(f"Admin: {user.admin}")
    ui.button("Save", on_click=update_user)

    if user.api_access:
        ui.separator()
        await list_keys()
