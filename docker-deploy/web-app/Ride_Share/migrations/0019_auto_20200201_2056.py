# Generated by Django 2.2.9 on 2020-02-01 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0018_auto_20200131_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='ride_status',
            field=models.CharField(blank=True, choices=[('opn', 'Open'), ('con', 'Confirmed'), ('cop', 'Completed')], default='opn', max_length=10),
        ),
    ]
