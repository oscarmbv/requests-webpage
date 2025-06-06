# Generated by Django 5.2 on 2025-04-24 15:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRecordsRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_code', models.CharField(editable=False, max_length=20, unique=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('partner_name', models.CharField(max_length=255)),
                ('user_groups_data', models.JSONField()),
                ('special_instructions', models.TextField(blank=True)),
                ('requested_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Records Request',
                'verbose_name_plural': 'User Records Requests',
            },
        ),
    ]
