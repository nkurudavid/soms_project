# Generated by Django 4.2.1 on 2023-06-07 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_trainee_cohort_alter_trainee_stack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainee',
            name='git_account',
            field=models.URLField(verbose_name='Git Account Link'),
        ),
    ]
