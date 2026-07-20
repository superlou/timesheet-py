import argparse
import asyncio
from pathlib import Path

from tortoise import Tortoise


async def install():
    parser = argparse.ArgumentParser()

    data_path = Path("./data")
    print(f"Clearing {data_path}...")
    for file in data_path.iterdir():
        file.unlink()

    data_path.mkdir()

    print("Initializing Tortoise...")
    await Tortoise.init(
        db_url="sqlite://./data/db.sqlite3", modules={"models": ["timesheet_py.models"]}
    )
    print("Generating schemas...")
    await Tortoise.generate_schemas()

    print("Done")

    await Tortoise.close_connections()


asyncio.run(install())
