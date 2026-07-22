from nicegui import APIRouter, app, ui

from timesheet_py.models import TimesheetEntry

router = APIRouter(prefix="/api")


@router.get("/entries")
async def get_entries():
    entries = (
        await TimesheetEntry()
        .all()
        .prefetch_related(
            "timesheet_row",
            "timesheet_row__project",
            "timesheet_row__activity",
            "timesheet_row__timesheet",
            "timesheet_row__timesheet__user",
        )
    )

    data = [
        {
            "date": entry.date,
            "hours": entry.hours,
            "project_name": entry.timesheet_row.project.name,
            "project_code": entry.timesheet_row.project.code,
            "activity_name": entry.timesheet_row.activity.name,
            "activity_code": entry.timesheet_row.activity.code,
            "user_name": entry.timesheet_row.timesheet.user.name,
            "user_email": entry.timesheet_row.timesheet.user.email,
            "user_employee_id": entry.timesheet_row.timesheet.user.employee_id,
            "submitted": entry.timesheet_row.timesheet.submitted,
            "approved": entry.timesheet_row.timesheet.approved,
        }
        for entry in entries
    ]
    return data
