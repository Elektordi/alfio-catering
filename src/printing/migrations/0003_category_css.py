# Generated by Django 4.1.7 on 2025-05-16 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('printing', '0002_badge_created_at_badge_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='css',
            field=models.TextField(default='/* FIXME */'),
        ),
    ]
