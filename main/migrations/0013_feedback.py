# Generated by Django 4.2.1 on 2023-06-10 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_delete_feedback'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.CharField(max_length=100, unique=True, verbose_name='Assignment Grade')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='main.assignmentreport', verbose_name='Assignment Report')),
            ],
        ),
    ]
