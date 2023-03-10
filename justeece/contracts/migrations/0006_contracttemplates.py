# Generated by Django 2.2.22 on 2021-12-16 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0005_auto_20211103_0059'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractTemplates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='Create Date')),
                ('modify_date', models.DateTimeField(auto_now=True, verbose_name='Modify Date')),
                ('title', models.CharField(max_length=40)),
                ('description', models.CharField(max_length=200)),
                ('logo', models.ImageField(upload_to='uploads/')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
