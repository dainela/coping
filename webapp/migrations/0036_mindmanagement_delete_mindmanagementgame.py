# Generated by Django 5.0.1 on 2024-11-23 04:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0035_mind'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MindManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mind_management_scores', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='MindManagementGame',
        ),
    ]
