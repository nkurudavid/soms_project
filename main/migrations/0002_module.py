# Generated by Django 4.2.1 on 2023-06-04 22:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Course Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('documentFiles', models.FileField(blank=True, null=True, upload_to='document/course/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'doc'])], verbose_name='Document')),
                ('stack', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='main.stack', verbose_name='Stack belonging')),
            ],
        ),
    ]
