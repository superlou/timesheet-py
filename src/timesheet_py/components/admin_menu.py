from nicegui import context, ui

MENU_LINKS = {
    "Timesheet Sets": "/admin/timesheet_sets",
    "Projects": "/admin/projects",
    "Activities": "/admin/activities",
    "Users": "/admin/users",
}


class AdminMenu(ui.element):
    def __init__(self):
        ui.context.client.sub_pages_router.on_path_changed(self.display.refresh)

    def __del__(self):
        print("DESTROYED")

    @ui.refreshable_method
    def display(self, path: str | None = None):
        if path is None:
            path = ui.context.client.sub_pages_router.current_path

        with ui.list().props("bordered separator"):
            ui.item_label("Admin").props("header").classes("text-bold")
            ui.separator()

            for label, target in MENU_LINKS.items():
                with ui.item(
                    on_click=lambda target=target: ui.navigate.to(target)
                ).classes("items-center") as item:
                    ui.label(label).props("active")

                    if path.startswith(target):
                        item.props("active")

        return self
