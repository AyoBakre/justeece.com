# Generated by Django 2.2.22 on 2021-12-05 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20211123_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cover_letter',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='about_me'),
        ),
    ]
