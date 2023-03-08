# Generated by Django 2.2.22 on 2022-03-31 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_allsearches_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maillmessage',
            name='group',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'INCOMPLETE_REGISTRANT'), (2, 'COMPLETE_REGISTRANT_WITH_REFERENCE'), (3, 'COMPLETE_REGISTRANT_WITHOUT_REFERENCE'), (4, 'REFERENCE_EMAIL_REMINDER')], null=True),
        ),
    ]