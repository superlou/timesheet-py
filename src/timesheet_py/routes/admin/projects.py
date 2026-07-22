from nicegui import ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.models import Project


class ProjectRow:
    def __init__(self, project: Project, editing: bool = False):
        self.project = project
        self.editing = editing

    @ui.refreshable_method
    def display(self):
        if self.editing:
            with ui.item_section():
                code_input = ui.input(value=self.project.code).props("dense")
            with ui.item_section():
                name_input = ui.input(value=self.project.name).props("dense")
            with ui.item_section():
                open_input = ui.checkbox(value=self.project.open).props("dense")
            with ui.item_section():
                ui.button(
                    icon="save",
                    on_click=lambda: self.save(
                        code_input.value, name_input.value, open_input.value
                    ),
                )
        else:
            with ui.item_section():
                ui.label(self.project.code)

            with ui.item_section():
                ui.label(self.project.name)

            with ui.item_section():
                ui.label("open" if self.project.open else "closed")

            with ui.item_section():
                ui.button(icon="edit", on_click=self.edit).props("flat dense")

    def edit(self):
        self.editing = True
        self.display.refresh()

    async def save(self, code: str, name: str, open: bool):
        self.project.code = code
        self.project.name = name
        self.project.open = open
        await self.project.save()
        self.editing = False
        self.display.refresh()


async def projects(user: CurrentUser):
    header(user)

    @ui.refreshable
    async def projects_list():
        projects = await Project.all()
        with ui.list().props("bordered separator").classes("w-full"):
            ui.item_label("Projects").props("header").classes("text-bold")
            ui.separator()

            for project in projects:
                with ui.item():
                    ProjectRow(project).display()

            with ui.item():
                with ui.item_section():
                    new_project_code = ui.input("Code").props("dense")
                with ui.item_section():
                    new_project_name = ui.input("Name").props("dense")
                with ui.item_section():
                    new_project_open = ui.checkbox().props("dense")

                with ui.item_section():
                    ui.button(icon="add", on_click=lambda: create_project()).props(
                        "flat dense"
                    )

            async def create_project():
                await Project.create(
                    code=new_project_code.value,
                    name=new_project_name.value,
                    open=new_project_open.value,
                )
                new_project_code.value = ""
                new_project_name.value = ""
                projects_list.refresh()

    await projects_list()
