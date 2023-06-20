# Generated by Django 4.2.2 on 2023-06-20 07:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_alter_assignment_documentfiles_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Company Name')),
                ('location', models.CharField(max_length=200, verbose_name='Location Address')),
                ('logoFile', models.ImageField(blank=True, null=True, upload_to='images/profile/', validators=[django.core.validators.FileExtensionValidator(['png', 'jpg', 'jpeg'])], verbose_name='Logo Image')),
            ],
        ),
    ]
