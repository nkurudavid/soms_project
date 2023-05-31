from django.contrib import admin
from .models import Cohort, Stack, Organization, OrganizationPosition, Trainer, Trainee, Outsource


# Register your models here.
admin.site.register(Cohort)
admin.site.register(Stack)
admin.site.register(Organization)
admin.site.register(OrganizationPosition)
admin.site.register(Trainer)
admin.site.register(Trainee)
admin.site.register(Outsource)
