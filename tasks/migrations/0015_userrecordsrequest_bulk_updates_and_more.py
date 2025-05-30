# Generated by Django 5.2 on 2025-04-27 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0014_remove_userrecordsrequest_blocked_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrecordsrequest',
            name='bulk_updates',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userrecordsrequest',
            name='manual_updated_properties',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userrecordsrequest',
            name='num_updated_properties',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userrecordsrequest',
            name='num_updated_users',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userrecordsrequest',
            name='operating_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userrecordsrequest',
            name='update_by_csv_rows',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
