# Generated by Django 4.2.1 on 2023-06-07 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0006_alter_application_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='githubLink',
            field=models.URLField(verbose_name='Git Account Link'),
        ),
    ]
