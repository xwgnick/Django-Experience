# Generated by Django 2.2.9 on 2020-02-04 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0023_auto_20200203_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email Address'),
        ),
    ]
