# Generated by Django 5.0.6 on 2024-05-16 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackdata',
            name='last_updated',
            field=models.DateTimeField(),
        ),
    ]
