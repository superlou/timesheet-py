from datetime import date
from pathlib import Path

import bcrypt
from nicegui import APIRouter, app, ui
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from ..models import (
    Activity,
    Project,
    Timesheet,
    TimesheetEntry,
    TimesheetRow,
    TimesheetSet,
    User,
)

router = APIRouter(prefix="/install")


@router.page("/")
async def install():
    data_path = Path("./data")

    async def run_setup():
        print("Deleting existing data...")
        for file in data_path.iterdir():
            file.unlink()
        data_path.mkdir(exist_ok=True)

        print("Generating schemas...")
        await Tortoise.close_connections()
        await Tortoise.init(
            db_url="sqlite://./data/db.sqlite3",
            modules={"models": ["timesheet_py.models"]},
        )
        await Tortoise.generate_schemas()

        print("Adding initial admin account...")
        password_hash = bcrypt.hashpw(
            password.value.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        await User.create(
            email=email.value,
            name=name.value,
            password_hash=password_hash,
            admin=True,
        )

        print("Loading demo data...")
        await load_demo_data()
        ui.notify("Installation completed!")

    ui.label("Initial admin account")
    name = ui.input("Name")
    email = ui.input("Email")
    password = ui.input("Password", password=True, password_toggle_button=True)

    ui.button("Set up", on_click=run_setup)


async def load_demo_data():
    await User.create(
        email="alice@test.com",
        name="Alice",
        employee_id="101",
        password_hash="test",
        admin=False,
    )
    await User.create(
        email="bob@test.com",
        name="Bob",
        employee_id="102",
        password_hash="test",
        admin=False,
    )
    await User.create(
        email="charlie@test.com",
        name="Charlie",
        employee_id="102",
        password_hash="test",
        admin=False,
    )

    ts = await TimesheetSet.create(
        start=date(2026, 7, 12),
        finish=date(2026, 7, 18),
        open=False,
    )
    await ts.submitters.add(*await User.all())
    for user in await User.all():
        await Timesheet.create(timesheet_set=ts, user=user, created_on=date.today())

    ts = await TimesheetSet.create(
        start=date(2026, 7, 12),
        finish=date(2026, 7, 18),
    )
    for user in await User.all():
        await Timesheet.create(timesheet_set=ts, user=user, created_on=date.today())

    a1 = await Activity.create(code="10", name="Engineering")
    a2 = await Activity.create(code="20", name="Training")
    a3 = await Activity.create(code="90", name="Vacation")

    p1 = await Project.create(code="1053.1", name="Fast Forward Project")
    p2 = await Project.create(code="1060.8", name="Rewind Project")
    p3 = await Project.create(code="5001.0", name="Vacation", open=False)

    ts = await Timesheet.get(user_id=1, timesheet_set__open=True)

    tr1 = await TimesheetRow.create(timesheet=ts, project=p1, activity=a1)
    await TimesheetEntry.create(timesheet_row=tr1, date=date(2026, 7, 13), hours=3)
    await TimesheetEntry.create(timesheet_row=tr1, date=date(2026, 7, 14), hours=5)

    tr2 = await TimesheetRow.create(timesheet=ts, project=p2, activity=a1)
    await TimesheetEntry.create(timesheet_row=tr2, date=date(2026, 7, 15), hours=8)
