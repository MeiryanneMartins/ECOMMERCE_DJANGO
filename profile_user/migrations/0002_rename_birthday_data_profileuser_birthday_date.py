# Generated by Django 4.2.5 on 2023-10-28 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile_user', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profileuser',
            old_name='birthday_data',
            new_name='birthday_date',
        ),
    ]
