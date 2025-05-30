# Generated by Django 5.2 on 2025-05-04 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0045_userrecordsrequest_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrecordsrequest',
            name='update_needed_flag',
            field=models.BooleanField(default=False, help_text='Indicates if the requester/team needs a progress update.', verbose_name='Update Needed Flag'),
        ),
    ]
