from django import forms
from django.core.validators import FileExtensionValidator
from phonenumber_field.formfields import PhoneNumberField

from account.models import User, Trainer


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'gender', 'is_manager', 'is_trainer', 'is_trainee', 'is_company']

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        fields = ['ssn', 'profilePicture', 'phone1', 'phone2', 'specialization', 'locationAddress']
