from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(Company)
admin.site.register(Cohort)
admin.site.register(Cohort_schedule)
admin.site.register(Stack)
admin.site.register(Module)
admin.site.register(Group)
admin.site.register(Assignment)
admin.site.register(AssignmentReport)
admin.site.register(Feedback)