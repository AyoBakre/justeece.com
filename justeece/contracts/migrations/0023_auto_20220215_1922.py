# Generated by Django 2.2.22 on 2022-02-15 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0022_auto_20220106_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracttemplate',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.DeleteModel(
            name='ContractTemplatesModel',
        ),
    ]