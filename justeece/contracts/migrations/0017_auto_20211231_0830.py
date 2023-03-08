# Generated by Django 2.2.22 on 2021-12-31 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0016_auto_20211231_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractsmodel',
            name='contract_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='create_contract_type', to='contracts.ContractTypeModel'),
        ),
    ]
