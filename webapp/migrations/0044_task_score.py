# Generated by Django 5.0.1 on 2024-11-23 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0043_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
