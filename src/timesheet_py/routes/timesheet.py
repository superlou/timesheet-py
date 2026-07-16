from nicegui import APIRouter, ui
from nicegui.ui import notify
from tortoise.transactions import in_transaction

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.components.timesheet_editor import TimesheetEditor, TimesheetEditorRow
from timesheet_py.models import (
    Activity,
    Project,
    TimesheetEntry,
    TimesheetRow,
    TimesheetSet,
    User,
)

router = APIRouter(prefix="/timesheet")


@router.page("/{timesheet_set_id}/me")
async def timesheet_for_current_user(timesheet_set_id: int, user: CurrentUser):
    header(user)

    timesheet_set = await TimesheetSet.get(id=timesheet_set_id)
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
        for r in await TimesheetRow.filter(
            timesheet_set=timesheet_set, user=user
        ).prefetch_related("entries", "project", "activity")
    ]

    TimesheetEditor(
        timesheet_set.dates,
        rows,
        {p.id: p.name for p in await Project.all()},
        {a.id: a.name for a in await Activity.all()},
    )

    ui.button("Save", on_click=lambda: save_timesheet(timesheet_set, user, rows))


async def save_timesheet(timesheet_set: TimesheetSet, user: User, rows):
    async with in_transaction() as conn:
        await TimesheetRow.filter(timesheet_set=timesheet_set, user=user).delete()

        for row in rows:
            timesheet_row = await TimesheetRow.create(
                timesheet_set=timesheet_set,
                user=user,
                project_id=row.project_id,
                activity_id=row.activity_id,
            )

            for date, hours in row.hours.items():
                await TimesheetEntry.create(
                    date=date, hours=hours, timesheet_row=timesheet_row
                )

    ui.notify("Timesheet saved.")
