# Generated by Django 2.2.9 on 2020-01-31 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0012_auto_20200131_0214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='sharable',
            field=models.CharField(choices=[('y', 'yes'), ('n', 'no')], max_length=3),
        ),
    ]
