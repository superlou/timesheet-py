from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='Activity',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('code', fields.CharField(max_length=255)),
                ('name', fields.CharField(max_length=255)),
            ],
            options={'table': 'activity', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Project',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('code', fields.CharField(max_length=255)),
                ('name', fields.CharField(max_length=255)),
                ('open', fields.BooleanField(default=True)),
            ],
            options={'table': 'project', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('email', fields.CharField(unique=True, max_length=255)),
                ('name', fields.CharField(default='', max_length=255)),
                ('employee_id', fields.CharField(default='', max_length=255)),
                ('password_hash', fields.CharField(max_length=255)),
                ('admin', fields.BooleanField(default=False)),
                ('approvers', fields.ManyToManyField('models.User', unique=True, db_constraint=True, through='user_approver', forward_key='user_id', backward_key='user_rel_id', related_name='approvees', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'user', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='TimesheetSet',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('start', fields.DateField()),
                ('finish', fields.DateField()),
                ('open', fields.BooleanField(default=True)),
                ('submitters', fields.ManyToManyField('models.User', unique=True, db_constraint=True, through='timesheetset_submitter', forward_key='user_id', backward_key='timesheetset_id', related_name='timesheet_sets', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'timesheetset', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Timesheet',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('timesheet_set', fields.ForeignKeyField('models.TimesheetSet', source_field='timesheet_set_id', db_constraint=True, to_field='id', related_name='timesheets', on_delete=OnDelete.CASCADE)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('saved_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('submitted_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
                ('approved_by', fields.ForeignKeyField('models.User', source_field='approved_by_id', null=True, db_constraint=True, to_field='id', related_name='timesheets_approved', on_delete=OnDelete.CASCADE)),
                ('approved_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'timesheet', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='TimesheetRow',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('timesheet', fields.ForeignKeyField('models.Timesheet', source_field='timesheet_id', db_constraint=True, to_field='id', related_name='timesheet_rows', on_delete=OnDelete.CASCADE)),
                ('project', fields.ForeignKeyField('models.Project', source_field='project_id', db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
                ('activity', fields.ForeignKeyField('models.Activity', source_field='activity_id', db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
            ],
            options={'table': 'timesheetrow', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='TimesheetEntry',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('timesheet_row', fields.ForeignKeyField('models.TimesheetRow', source_field='timesheet_row_id', db_constraint=True, to_field='id', related_name='entries', on_delete=OnDelete.CASCADE)),
                ('date', fields.DateField()),
                ('hours', fields.FloatField()),
            ],
            options={'table': 'timesheetentry', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
