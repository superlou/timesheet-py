from nicegui import ui

from timesheet_py.models import User

from .. import auth


def header(user: User):
    with ui.header().classes("items-center justify-between"):
        with ui.link(target="/").classes("text-white"):
            ui.icon("home")

        with ui.row().classes("items-center"):
            with ui.link(target="/user"):
                with ui.row().classes("text-white items-center"):
                    ui.icon("person")
                    ui.label(user.email)

            ui.button(on_click=auth.logout, icon="logout")
