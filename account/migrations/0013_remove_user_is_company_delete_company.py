# Generated by Django 4.2.2 on 2023-06-20 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_trainee_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_company',
        ),
        migrations.DeleteModel(
            name='Company',
        ),
    ]
