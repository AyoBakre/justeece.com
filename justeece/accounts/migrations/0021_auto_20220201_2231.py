# Generated by Django 2.2.22 on 2022-02-01 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20220201_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='ddf/'),
        ),
    ]