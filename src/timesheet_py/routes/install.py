import shutil
from pathlib import Path
import bcrypt
from nicegui import ui, APIRouter
from tortoise import Tortoise
from ..models import User

router = APIRouter(prefix="/install")

@router.page("/")
async def install():
    data_path = Path("./data")

    async def run_setup():
        shutil.rmtree(data_path)
        data_path.mkdir(exist_ok=True)
        await Tortoise.generate_schemas()

        password_hash = bcrypt.hashpw(
            password.value.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        await User.create(
            email=email.value,
            password_hash=password_hash,
            admin=True,
        )
        ui.navigate.to("/login")

    ui.label("Initial admin account")
    email = ui.input("Email")
    password = ui.input("Password", password=True, password_toggle_button=True)

    ui.button("Set up", on_click=run_setup)
