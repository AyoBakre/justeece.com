# Generated by Django 2.2.22 on 2021-11-15 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20211101_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailmessage',
            name='from_email',
            field=models.CharField(default='admin@justeece.com', max_length=500),
        ),
    ]
