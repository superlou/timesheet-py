from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0006_add_one_or_two_name_selection")]

    initial = False

    operations = [ops.RunSQL("DELETE FROM timesheetentry WHERE hours = 0;")]
