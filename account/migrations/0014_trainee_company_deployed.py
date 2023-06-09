# Generated by Django 4.2.2 on 2023-06-20 08:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_company'),
        ('account', '0013_remove_user_is_company_delete_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainee',
            name='company_deployed',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='trainees', to='main.company', verbose_name='Company Deployed'),
        ),
    ]
