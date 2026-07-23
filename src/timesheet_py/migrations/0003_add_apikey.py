from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_rename_employee_id_to_code')]

    initial = False

    operations = [
        ops.CreateModel(
            name='APIKey',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', on_delete=OnDelete.CASCADE)),
                ('key', fields.CharField(max_length=255)),
            ],
            options={'table': 'apikey', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
    ]
