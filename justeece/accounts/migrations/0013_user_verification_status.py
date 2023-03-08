# Generated by Django 2.2.22 on 2022-01-16 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20220115_0947'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_status',
            field=models.IntegerField(choices=[(1, 'Stage 1'), (2, 'Stage 2'), (3, 'Stage 3')], default=1, verbose_name='Verification Status'),
        ),
    ]
