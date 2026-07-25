from tortoise import migrations
from tortoise.migrations import operations as ops

class Migration(migrations.Migration):
    dependencies = [('models', '0004_add_api_access_flag')]

    initial = False

    operations = [
        ops.RemoveField(model_name='TimesheetSet', name='submitters'),
    ]
