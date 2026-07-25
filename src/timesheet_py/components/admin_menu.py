from nicegui import ui


def admin_menu():
    with ui.list().props("bordered separator"):
        ui.item_label("Admin").props("header").classes("text-bold")
        ui.separator()

        with ui.item().classes("items-center"):
            ui.link("Timesheet Sets", "/admin/timesheet_sets")

        with ui.item().classes("items-center"):
            ui.link("Projects", "/admin/projects")

        with ui.item().classes("items-center"):
            ui.link("Activities", "/admin/activities")

        with ui.item().classes("items-center"):
            ui.link("Users", "/admin/users")
