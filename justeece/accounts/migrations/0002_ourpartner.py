# Generated by Django 2.2.22 on 2021-11-15 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OurPartner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Company_name', models.CharField(blank=True, max_length=300, null=True)),
                ('Founder', models.CharField(blank=True, max_length=300, null=True)),
                ('Image_url', models.CharField(max_length=300, null=True)),
            ],
        ),
    ]