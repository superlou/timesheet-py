from datetime import date, timedelta

from tortoise.fields import (
    BooleanField,
    CharField,
    DateField,
    FloatField,
    ForeignKeyField,
    IntField,
    ManyToManyField,
    OnDelete,
)
from tortoise.models import Model


class User(Model):
    id = IntField(pk=True)
    email = CharField(max_length=255, unique=True)
    name = CharField(max_length=255, default="")
    employee_id = CharField(max_length=255, default="")
    password_hash = CharField(max_length=255)
    admin = BooleanField(default=False)
    approvers = ManyToManyField(
        "models.User", related_name="approvees", through="user_approver"
    )


class TimesheetSet(Model):
    id = IntField(pk=True)
    start = DateField()
    finish = DateField()
    open = BooleanField(default=True)
    submitters = ManyToManyField(
        "models.User",
        related_name="timesheet_sets",
        through="timesheetset_submitter",
    )

    @property
    def dates(self) -> list[date]:
        num_days = (self.finish - self.start).days + 1
        return [self.start + timedelta(days=i) for i in range(num_days)]


class TimesheetRow(Model):
    id = IntField(pk=True)
    timesheet_set = ForeignKeyField("models.TimesheetSet")
    user = ForeignKeyField("models.User")
    project = ForeignKeyField("models.Project")
    activity = ForeignKeyField("models.Activity")


class TimesheetEntry(Model):
    id = IntField(pk=True)
    timesheet_row = ForeignKeyField(
        "models.TimesheetRow",
        related_name="entries",
        on_delete=OnDelete.CASCADE,
    )
    date = DateField()
    hours = FloatField()


class Project(Model):
    id = IntField(pk=True)
    code = CharField(max_length=255)
    name = CharField(max_length=255)
    open = BooleanField(default=True)


class Activity(Model):
    id = IntField(pk=True)
    code = CharField(max_length=255)
    name = CharField(max_length=255)
