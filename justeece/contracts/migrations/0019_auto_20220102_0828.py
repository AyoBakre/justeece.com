# Generated by Django 2.2.22 on 2022-01-02 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0018_auto_20220102_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracttemplate',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
