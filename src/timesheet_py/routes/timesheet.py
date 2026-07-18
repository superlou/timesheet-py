from datetime import datetime

from fastapi import HTTPException
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


def can_view_timesheet(timesheet: Timesheet, current_user: CurrentUser) -> bool:
    return timesheet.user == current_user or current_user in timesheet.user.approvers


@router.page("/{timesheet_id}")
async def timesheet(timesheet_id: int, current_user: CurrentUser):
    header(current_user)

    timesheet = await Timesheet.get(id=timesheet_id).prefetch_related(
        "timesheet_set",
        "timesheet_rows",
        "approved_by",
        "timesheet_rows__project",
        "timesheet_rows__activity",
        "timesheet_rows__entries",
        "user",
        "user__approvers",
    )
    timesheet_set = timesheet.timesheet_set

    if not can_view_timesheet(timesheet, current_user):
        raise HTTPException(status_code=403)

    ui.label(
        f"Timesheet for {timesheet.user.name}, {timesheet_set.start} to {timesheet_set.finish}"
    )

    @ui.refreshable
    def actions():
        with ui.button_group():
            if not timesheet_set.open:
                pass
            elif timesheet.approved:
                ui.button("Save").props("disabled")
                ui.button("Edit", on_click=lambda: edit_timesheet(timesheet))
                if current_user in timesheet.user.approvers:
                    ui.button("Unapprove", on_click=lambda: unapprove_timesheet())
            elif timesheet.submitted:
                ui.button("Save").props("disabled")
                ui.button("Edit", on_click=lambda: edit_timesheet(timesheet))
                if current_user in timesheet.user.approvers:
                    ui.button("Approve", on_click=lambda: approve_timesheet())
            else:
                ui.button("Save", on_click=lambda: save_timesheet(timesheet, rows))
                ui.button("Submit", on_click=lambda: submit_timesheet(timesheet))

    actions()

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
        (timesheet, "editable"),
    )

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

    async def submit_timesheet(timesheet: Timesheet):
        await save_timesheet(timesheet, rows)
        timesheet.submitted_at = datetime.now()
        await timesheet.save()
        actions.refresh()

    async def edit_timesheet(timesheet: Timesheet):
        timesheet.submitted_at = None
        timesheet.approved_at = None
        timesheet.approved_by = None
        await timesheet.save()
        actions.refresh()

    async def approve_timesheet():
        timesheet.approved_at = datetime.now()
        timesheet.approved_by = current_user
        await timesheet.save()
        actions.refresh()

    async def unapprove_timesheet():
        timesheet.approved_at = None
        timesheet.approved_by = None
        await timesheet.save()
        actions.refresh()
