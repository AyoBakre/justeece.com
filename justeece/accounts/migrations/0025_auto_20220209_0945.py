# Generated by Django 2.2.22 on 2022-02-09 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0024_referencerequestid_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reference',
            name='profile_photo',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/'),
        ),
    ]
