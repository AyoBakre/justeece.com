# Generated by Django 2.2.22 on 2021-12-31 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0014_auto_20211231_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractsmodel',
            name='contract_end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]