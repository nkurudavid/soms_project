# Generated by Django 4.2.1 on 2023-06-07 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0004_alter_application_githublink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.BooleanField(default=False, verbose_name='Status'),
        ),
    ]
