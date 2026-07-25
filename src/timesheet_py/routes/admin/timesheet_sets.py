from nicegui import ui
from tortoise.transactions import in_transaction

from timesheet_py.api import router
from timesheet_py.auth import CurrentUser
from timesheet_py.components.admin_menu import admin_menu
from timesheet_py.components.header import header
from timesheet_py.models import Timesheet, TimesheetSet, User


async def timesheet_sets(user: CurrentUser):
    @ui.refreshable
    async def timesheets_list_items(timesheet_sets: list[TimesheetSet]):
        for timesheet_set in timesheet_sets:
            with ui.item():
                with ui.item_section():
                    with ui.row().classes("items-center gap-2"):
                        ui.icon("adjust" if timesheet_set.open else "check_circle")
                        ui.label(f"{timesheet_set.start} - {timesheet_set.finish}")

                with ui.item_section():
                    num_submitters = len(timesheet_set.timesheets)
                    with ui.row().classes("items-center gap-2"):
                        ui.label(f"{num_submitters}")
                        ui.icon("person")

                with ui.item_section().classes("col-shrink"):
                    ui.button(
                        icon="edit",
                        on_click=lambda: ui.navigate.to(
                            f"/admin/timesheet_sets/{timesheet_set.id}"
                        ),
                    ).props("flat")

    async def filter_timesheet_sets():
        pass

    header(user)
    with ui.row().classes("w-full"):
        with ui.column().classes("col-2"):
            admin_menu()
        with ui.column().classes("col-9"):
            ui.label("Timesheet Sets")
            ui.link("New", timesheets_sets_new)

            with ui.list().props("bordered separator").classes("w-full"):
                with ui.item_label().props("header").classes("text-bold"):
                    ui.label("Timesheet Sets")

                ui.separator()

                filters = {}
                timesheet_sets = (
                    await TimesheetSet.filter(**filters)
                    .all()
                    .prefetch_related("timesheets")
                )

                await timesheets_list_items(timesheet_sets)


async def timesheets_sets_new(user: CurrentUser):
    async def create_timesheet_set():
        start, finish = date_range.value.split(" - ")
        timesheet_set = TimesheetSet(start=start, finish=finish, open=True)

        async with in_transaction() as _conn:
            await timesheet_set.save()

            for user, checkbox in submitters.items():
                if checkbox.value:
                    await Timesheet.create(
                        timesheet_set=timesheet_set,
                        user=user,
                    )

        ui.navigate.to(timesheet_sets)

    header(user)

    with ui.row().classes("w-full"):
        with ui.column().classes("col-2"):
            admin_menu()
        with ui.column().classes("col-9"):
            ui.label("New Timesheet")

            with ui.row():
                with ui.column():
                    ui.label("Dates")
                    date_range = ui.date_input("Range", range_input=True)
                    ui.button("Create timesheet", on_click=create_timesheet_set)

                with ui.column():
                    ui.label("Submitters")
                    submitters = {
                        user: ui.checkbox(f"{user.name} ({user.email})", value=True)
                        for user in await User.all()
                    }


async def timesheet_sets_edit(timesheet_set_id: int, user: CurrentUser):
    async def delete():
        await timesheet_set.delete()
        ui.navigate.to(timesheet_sets)

    async def save():
        start, finish = date_range.value.split(" - ")
        timesheet_set.start = start
        timesheet_set.finish = finish
        timesheet_set.open = is_open.value

        for user_id, user_selected in user_selection.items():
            user = await User.get(id=user_id)
            if user_selected and user not in timesheet_set_users:
                await Timesheet.create(
                    timesheet_set=timesheet_set,
                    user=user,
                )
            if not user_selected and user in timesheet_set_users:
                await Timesheet.filter(timesheet_set=timesheet_set, user=user).delete()

        await timesheet_set.save()
        ui.notify("Saved timesheet set")

    with ui.dialog() as delete_dialog, ui.card():
        with ui.card_section():
            ui.label("Delete Timesheet Set?").classes("text-h6")

        with ui.card_section():
            ui.label(
                "This will delete all timesheets and data associatied with this timesheet set."
            )

        with ui.card_section():
            with ui.row():
                ui.button("Cancel", on_click=delete_dialog.close)
                ui.button("Delete", on_click=delete)

    header(user)

    timesheet_set = await TimesheetSet.get(id=timesheet_set_id).prefetch_related(
        "timesheets", "timesheets__user"
    )

    with ui.row().classes("w-full"):
        with ui.column().classes("col-2"):
            admin_menu()
        with ui.column().classes("col-9"):
            with ui.row():
                with ui.column():
                    with ui.row().classes("items-center").classes("w-full"):
                        ui.label("Timesheet Set")
                        ui.label().classes("col-grow")
                        ui.button(
                            icon="delete", on_click=lambda: delete_dialog.open()
                        ).props("outline")

                    date_range = ui.date_input(
                        "Range",
                        range_input=True,
                        value=f"{timesheet_set.start} - {timesheet_set.finish}",
                    )
                    is_open = ui.checkbox("Open", value=timesheet_set.open)
                    ui.button("Save", on_click=save)

                    timesheet_set_users = [
                        timesheet.user for timesheet in timesheet_set.timesheets
                    ]
                    users = await User.all()
                    user_selection = {
                        str(user.id): user in timesheet_set_users for user in users
                    }

                with ui.column():
                    with ui.list().props("bordered separator").classes("w-full"):
                        ui.item_label("Timesheets").props("header").classes("text-bold")
                        ui.separator()

                        for user in users:
                            with ui.item():
                                with ui.item_section():
                                    ui.checkbox(user.name).bind_value(
                                        user_selection, str(user.id)
                                    )
