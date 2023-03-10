# Generated by Django 2.2.22 on 2022-01-21 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20211215_0946'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaillMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('modify_date', models.DateTimeField(auto_now=True, verbose_name='Modify Date')),
                ('title', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=250)),
                ('body', models.TextField(max_length=1050)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
