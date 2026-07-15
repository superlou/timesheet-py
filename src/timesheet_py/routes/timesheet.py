from nicegui import APIRouter, ui

from timesheet_py.auth import CurrentUser
from timesheet_py.components.header import header
from timesheet_py.components.timesheet_editor import TimesheetEditor, TimesheetEditorRow
from timesheet_py.models import Activity, Project, TimesheetRow, TimesheetSet

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
            project_name=r.project.name,
            activity_id=r.activity.id,
            activity_name=r.activity.name,
            hours={
                d: sum(entry.hours for entry in r.entries if entry.date == d)
                for d in timesheet_set.dates
            },
        )
        for r in await TimesheetRow.filter(
            timesheet_set=timesheet_set, user=user
        ).prefetch_related("entries", "project", "activity")
    ]
    timesheet_editor = TimesheetEditor(
        timesheet_set.dates,
        rows,
        {p.id: p.name for p in await Project.all()},
        {a.id: a.name for a in await Activity.all()},
    )
