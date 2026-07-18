from datetime import datetime

from nicegui import APIRouter, ui
from tortoise.transactions import in_transaction

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.components.timesheet_editor import TimesheetEditor, TimesheetEditorRow
from timesheet_py.models import (
    Activity,
    Project,
    Timesheet,
    TimesheetEntry,
    TimesheetRow,
)

router = APIRouter(prefix="/timesheet")


@router.page("/{timesheet_id}")
async def timesheet(timesheet_id: int, user: CurrentUser):
    header(user)

    timesheet = await Timesheet.get(id=timesheet_id).prefetch_related(
        "timesheet_set",
        "timesheet_rows",
        "timesheet_rows__project",
        "timesheet_rows__activity",
        "timesheet_rows__entries",
    )
    timesheet_set = timesheet.timesheet_set

    ui.label(
        f"Timesheet for {user.name}, {timesheet_set.start} to {timesheet_set.finish}"
    )

    rows = [
        TimesheetEditorRow(
            project_id=r.project.id,
            activity_id=r.activity.id,
            hours={
                d: sum(entry.hours for entry in r.entries if entry.date == d)
                for d in timesheet_set.dates
            },
        )
        for r in timesheet.timesheet_rows
    ]

    TimesheetEditor(
        timesheet_set.dates,
        rows,
        {p.id: p.name for p in await Project.all()},
        {a.id: a.name for a in await Activity.all()},
    )

    ui.button("Save", on_click=lambda: save_timesheet(timesheet, rows))
    ui.label().bind_text_from(timesheet, "saved_at", lambda x: f"Last saved on {x}")


async def save_timesheet(timesheet: Timesheet, rows):
    async with in_transaction() as _conn:
        await TimesheetRow.filter(timesheet=timesheet).delete()

        for row in rows:
            timesheet_row = await TimesheetRow.create(
                timesheet=timesheet,
                project_id=row.project_id,
                activity_id=row.activity_id,
            )

            for date, hours in row.hours.items():
                await TimesheetEntry.create(
                    date=date, hours=hours, timesheet_row=timesheet_row
                )

        timesheet.saved_at = datetime.now()
        await timesheet.save()

    ui.notify("Timesheet saved.")
