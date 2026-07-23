from tortoise import fields, migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0003_add_apikey")]

    initial = False

    operations = [
        ops.AddField(
            model_name="User",
            name="api_access",
            field=fields.BooleanField(db_default=False),
        ),
    ]
