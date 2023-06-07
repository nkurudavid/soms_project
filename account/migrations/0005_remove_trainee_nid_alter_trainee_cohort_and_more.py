# Generated by Django 4.2.1 on 2023-06-06 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_module'),
        ('account', '0004_remove_programmanager_bio_remove_programmanager_dob_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainee',
            name='nid',
        ),
        migrations.AlterField(
            model_name='trainee',
            name='cohort',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trainees', to='main.cohort', verbose_name='Cohort belonging'),
        ),
        migrations.AlterField(
            model_name='trainee',
            name='stack',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='trainees', to='main.stack', verbose_name='Stack belonging'),
        ),
    ]