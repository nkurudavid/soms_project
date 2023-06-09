# Generated by Django 4.2.1 on 2023-06-07 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='cohort',
            name='status',
            field=models.CharField(choices=[('Waiting', 'Waiting'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Waiting', max_length=10, verbose_name='Status'),
        ),
        migrations.CreateModel(
            name='Cohort_schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('schedule_name', models.CharField(choices=[('', 'Select Schedule'), ('Application', 'Application'), ('Graduation', 'Graduation')], default='', max_length=12, verbose_name='Status')),
                ('start_period', models.DateTimeField()),
                ('end_period', models.DateTimeField()),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='schedules', to='main.cohort', verbose_name='Cohort Scheduled')),
            ],
        ),
    ]
