from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import Activity


class ActivityRow:
    def __init__(self, activity: Activity, editing: bool = False):
        self.activity = activity
        self.editing = editing

    @ui.refreshable_method
    def display(self):
        if self.editing:
            with ui.item_section():
                code_input = ui.input(value=self.activity.code).props("dense")
            with ui.item_section():
                name_input = ui.input(value=self.activity.name).props("dense")
            # with ui.item_section():
            #     open_input = ui.checkbox(value=self.activity.open).props("dense")
            with ui.item_section():
                ui.button(
                    icon="save",
                    on_click=lambda: self.save(
                        code_input.value,
                        name_input.value,  # , open_input.value
                    ),
                )
        else:
            with ui.item_section():
                ui.label(self.activity.code)

            with ui.item_section():
                ui.label(self.activity.name)

            # with ui.item_section():
            #     ui.label("open" if self.activity.open else "closed")

            with ui.item_section():
                ui.button(icon="edit", on_click=self.edit).props("flat dense")

    def edit(self):
        self.editing = True
        self.display.refresh()

    async def save(self, code: str, name: str):  # , open: bool):
        self.activity.code = code
        self.activity.name = name
        self.activity.open = open
        await self.activity.save()
        self.editing = False
        self.display.refresh()


async def activities(user: CurrentUser):
    header(user)

    @ui.refreshable
    async def activities_list():
        activities = await Activity.all()
        with ui.list().props("bordered separator").classes("w-full"):
            ui.item_label("Activities").props("header").classes("text-bold")
            ui.separator()

            for activity in activities:
                with ui.item():
                    ActivityRow(activity).display()

            with ui.item():
                with ui.item_section():
                    new_activity_code = ui.input("Code")

                with ui.item_section():
                    new_activity_name = ui.input("Name")

                with ui.item_section():
                    ui.button(icon="add", on_click=lambda: create_activity()).props(
                        "flat dense"
                    )

        async def create_activity():
            await Activity.create(
                code=new_activity_code.value, name=new_activity_name.value
            )
            new_activity_code.value = ""
            new_activity_name.value = ""
            activities_list.refresh()

    await activities_list()
