from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    name = fields.CharField(max_length=255, unique=True, default="")
    employee_id = fields.CharField(max_length=255, unique=True, default="")
    password_hash = fields.CharField(max_length=255)
    admin = fields.BooleanField(default=False)
