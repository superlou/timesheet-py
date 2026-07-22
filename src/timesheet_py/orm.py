TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://./data/db.sqlite3",
    },
    "apps": {
        "models": {
            "models": ["timesheet_py.models"],
            "default_connection": "default",
            "migrations": "timesheet_py.migrations",
        }
    },
}
