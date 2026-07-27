from typing import Any

from nicegui import ui

from timesheet_py.models import Setting, User


async def convert_to_split_name():
    users = await User.all()

    for user in users:
        parts = user.name.split(" ", maxsplit=1)
        if len(parts) > 1:
            user.name = parts[0]
            user.last_name = parts[1]

        await user.save()


async def convert_to_single_name():
    users = await User.all()

    for user in users:
        user.name = (user.name + " " + user.last_name).strip()
        user.last_name = ""
        await user.save()


async def save(new_setting: dict[str, Any]):
    split_name = await Setting.get(key="split_name")

    if new_setting["split_name"] and split_name.value == "0":
        await convert_to_split_name()
        split_name.value = "1"
        await split_name.save()
    elif not new_setting["split_name"] and split_name.value == "1":
        await convert_to_single_name()
        split_name.value = "0"
        await split_name.save()

    ui.notify("Saved settings")


async def edit_settings(user):
    ui.label("Settings")

    settings = {}

    split_name = await Setting.get(key="split_name")
    settings["split_name"] = split_name.value == "1"
    with ui.checkbox().bind_value(settings, "split_name"):
        with ui.column().classes("gap-0"):
            ui.html("Split name")
            ui.html(split_name.description).classes("text-caption")

    ui.button("Save", on_click=lambda: save(settings))
