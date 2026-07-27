from tortoise import fields, migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0005_remove_submitters")]

    initial = False

    operations = [
        ops.CreateModel(
            name="Setting",
            fields=[
                (
                    "key",
                    fields.CharField(
                        primary_key=True, unique=True, db_index=True, max_length=255
                    ),
                ),
                ("value", fields.TextField(unique=False)),
                ("description", fields.TextField(unique=False)),
            ],
            options={"table": "setting", "app": "models", "pk_attr": "key"},
            bases=["Model"],
        ),
        ops.AddField(
            model_name="User",
            name="last_name",
            field=fields.CharField(db_default="", max_length=255),
        ),
        ops.RunSQL(
            sql="INSERT INTO setting (key, value, description) VALUES ('split_name', '0', 'Separate name into a first name and last name field.');",
            reverse_sql="DELETE FROM setting WHERE key = 'split_name';",
        ),
    ]
