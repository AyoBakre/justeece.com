# Generated by Django 2.2.22 on 2021-11-01 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_cancelcontractreasonchoicemodel_contractclosefeedback_endcontractreasonchoicemodel_rejectcontractrea'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractclosefeedback',
            name='status',
            field=models.SmallIntegerField(choices=[(1, 'Reject Contract'), (2, 'Accept Contract'), (3, 'End Contract'), (4, 'Cancel Contract')]),
        ),
    ]