from fastapi import Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from nicegui import APIRouter, app

from timesheet_py.models import APIKey, TimesheetEntry

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def validate_api_key(api_key: str = Security(api_key_header)):
    key = await APIKey.filter(key=api_key).first().prefetch_related("user")

    if key is not None and key.user.api_access:
        return key.key

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing API Key",
    )


router = APIRouter(prefix="/api", dependencies=[Depends(validate_api_key)])
app.docs_url = "/api/docs"


@router.get("/entries")
async def get_entries() -> JSONResponse:
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
            "user_code": entry.timesheet_row.timesheet.user.code,
            "submitted": entry.timesheet_row.timesheet.submitted,
            "approved": entry.timesheet_row.timesheet.approved,
        }
        for entry in entries
    ]
    return JSONResponse(jsonable_encoder(data))
