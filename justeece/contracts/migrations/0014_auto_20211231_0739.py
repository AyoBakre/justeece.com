# Generated by Django 2.2.22 on 2021-12-31 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0013_auto_20211223_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractsmodel',
            name='contract_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
