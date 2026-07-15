from dataclasses import dataclass
from datetime import date

from nicegui import ui
from nicegui.element import Element


@dataclass
class TimesheetEditorRow:
    project_id: int
    project_name: str
    activity_id: int
    activity_name: str
    hours: dict[date, float]


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
        self.projects = projects
        self.activities = activities
        self.render()

    @ui.refreshable_method
    def render(self) -> None:
        with ui.grid(columns=len(self.dates) + 3).classes("items-center"):
            ui.label("Project")
            ui.label("Code")

            for date in self.dates:
                ui.label(f"{date.strftime('%a')} {date.month}/{date.day}")

            ui.label("Total")

            for row in self.rows:
                self.render_row(row)

        ui.button("Save")

    @ui.refreshable_method
    def render_row(self, row: TimesheetEditorRow):
        ui.select(self.projects).bind_value(row, "project_id")
        ui.select(self.activities).bind_value(row, "activity_id")

        for d in self.dates:
            value = str(row.hours[d] or "")
            ui.input(value=value).props("outlined")

        value = str(sum(row.hours.values())) or ""
        ui.label(value)
