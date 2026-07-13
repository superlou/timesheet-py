from tortoise.fields import (
    BooleanField,
    CharField,
    DateField,
    ForeignKeyField,
    IntField,
    ManyToManyField,
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


class Project(Model):
    id = IntField(pk=True)
    code = CharField(max_length=255)
    name = CharField(max_length=255)
    open = BooleanField(default=True)


class Activity(Model):
    id = IntField(pk=True)
    code = CharField(max_length=255)
    name = CharField(max_length=255)
