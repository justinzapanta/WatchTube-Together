# Generated by Django 5.1.5 on 2025-01-19 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_room_room_video_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='room_visitor',
            field=models.JSONField(null=True),
        ),
    ]
