# Generated by Django 5.2 on 2025-04-27 17:55

import django.db.models.deletion
import django.utils.timezone
import tasks.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0013_userrecordsrequest_blocked_by_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='blocked_at',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='blocked_by',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='blocked_reason',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='qa_resolved',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='reject_reason',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='rejected_at',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='rejected_by',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='resolve_message',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='resolved_at',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='resolved_by',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='resolved_file',
        ),
        migrations.RemoveField(
            model_name='userrecordsrequest',
            name='resolved_link',
        ),
        migrations.CreateModel(
            name='BlockedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.TextField()),
                ('blocked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_messages', to='tasks.userrecordsrequest')),
            ],
            options={
                'ordering': ['blocked_at'],
            },
        ),
        migrations.CreateModel(
            name='RejectedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rejected_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('reason', models.TextField()),
                ('is_resolved_qa', models.BooleanField(default=False)),
                ('rejected_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rejected_messages', to='tasks.userrecordsrequest')),
            ],
            options={
                'ordering': ['rejected_at'],
            },
        ),
        migrations.CreateModel(
            name='ResolvedMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resolved_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('message', models.TextField()),
                ('resolved_file', models.FileField(blank=True, null=True, upload_to='user_records/resolutions/', validators=[tasks.validators.validate_file_size])),
                ('resolved_link', models.URLField(blank=True, null=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resolved_messages', to='tasks.userrecordsrequest')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['resolved_at'],
            },
        ),
    ]
