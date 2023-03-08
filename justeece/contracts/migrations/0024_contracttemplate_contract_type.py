# Generated by Django 2.2.22 on 2022-02-15 19:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0023_auto_20220215_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='contracttemplate',
            name='contract_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contract_type', to='contracts.ContractTypeModel'),
        ),
    ]
