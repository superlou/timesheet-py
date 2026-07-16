from dataclasses import dataclass
from datetime import date

from nicegui import ui
from nicegui.element import Element


@dataclass
class TimesheetEditorRow:
    project_id: int
    activity_id: int
    hours: dict[date, float]

    @property
    def total_hours(self) -> float:
        return sum(self.hours.values())

    def set_hours_from_text(self, d: date, value: str):
        try:
            if value == "":
                self.hours[d] = 0
            else:
                self.hours[d] = float(value)
        except ValueError:
            pass


class TimesheetEditor(Element):
    def __init__(
        self,
        dates: list[date],
        rows: list[TimesheetEditorRow],
        projects: dict[int, str],
        activities: dict[int, str],
    ):
        self.dates = dates
        self.rows = rows
        self.projects = {-1: ""} | projects
        self.activities = {-1: ""} | activities
        self.render()

    @ui.refreshable_method
    def render(self) -> None:
        with ui.grid(columns=len(self.dates) + 4).classes("items-center"):
            self.render_header()

            for row in self.rows:
                self.render_row(row)

            self.render_totals()

    def render_header(self):
        ui.label("Project")
        ui.label("Code")

        for d in self.dates:
            ui.label(f"{d.strftime('%a')} {d.month}/{d.day}")

        ui.label("Total")
        ui.label("")

    @ui.refreshable_method
    def render_row(self, row: TimesheetEditorRow):
        ui.select(self.projects).bind_value(row, "project_id")
        ui.select(self.activities).bind_value(row, "activity_id")

        for d in self.dates:
            value = str(row.hours[d] or "")
            ui.input(value=value).props("outlined").on_value_change(
                lambda evt, d=d: row.set_hours_from_text(d, evt.value)
            ).on_value_change(self.render_totals.refresh)

        ui.label().bind_text(row, "total_hours")
        ui.button(icon="delete", on_click=lambda: self.delete_row(row))

    @ui.refreshable_method
    def render_totals(self):
        ui.label("")
        ui.label("")

        all_hours = []

        for column_date in self.dates:
            date_hours = sum(
                row.hours[date]
                for row in self.rows
                for date in row.hours
                if date == column_date
            )
            ui.label(str(date_hours))
            all_hours.append(date_hours)

        ui.label(str(sum(all_hours)))
        ui.button(icon="add", on_click=self.add_row)

    def add_row(self):
        self.rows.append(
            TimesheetEditorRow(
                project_id=-1,
                activity_id=-1,
                hours={d: 0 for d in self.dates},
            )
        )
        self.render.refresh()

    def delete_row(self, row: TimesheetEditorRow):
        self.rows.remove(row)
        self.render.refresh()
