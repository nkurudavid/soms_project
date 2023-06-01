from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Trainer, Trainee, ProgramManager, Company

# Register your models here.@admin.register(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'gender', 'is_active', 'last_login')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter =('is_manager','is_trainer','is_trainee','is_company','is_superuser', 'is_active')
    fieldsets = (
        ('User Credential', {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'gender', ('is_manager','is_trainer','is_trainee','is_company',),)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        ('New User', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'gender', ('is_manager','is_trainer','is_trainee','is_company',),),
        }),
        ('Permission', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser',),
        }),
        ('User Credential', {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',),
        }),
    )
    ordering =('email',)


admin.site.register(Trainer)
admin.site.register(Trainee)
admin.site.register(ProgramManager)
admin.site.register(Company)