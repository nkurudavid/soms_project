from django.utils.safestring import mark_safe
from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.db import models

from . manager import UserManager
from main.models import Stack, Cohort


# Create your models here.
class User(AbstractUser):
    class Gender(models.TextChoices):
        SELECT = "", "Select Gender"
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    first_name = models.CharField(verbose_name="First Name", max_length=50, blank=False)
    last_name = models.CharField(verbose_name="Last Name", max_length=50, blank=False)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True, blank=False)
    gender = models.CharField(verbose_name="Gender", choices=Gender.choices, default=Gender.SELECT, max_length=10)
    is_manager = models.BooleanField(verbose_name="Is Manager", default=False)
    is_trainer = models.BooleanField(verbose_name="Is Trainer", default=False)
    is_trainee = models.BooleanField(verbose_name="Is Trainee", default=False)
    is_company = models.BooleanField(verbose_name="Is Compony", default=False)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    # update django about user model
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)



class Trainer(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="trainers", on_delete=models.CASCADE)
    ssn = models.CharField(verbose_name="SSN", max_length=100, blank=True, null=True)
    profilePicture = models.ImageField(
        verbose_name="Image", 
        upload_to="images/profile/", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        blank=True, null=True
    )
    phone1 = PhoneNumberField(verbose_name="Phone 1", blank=True)
    phone2 = PhoneNumberField(verbose_name="Phone 2", blank=True)
    specialization = models.CharField(verbose_name="Specializations", max_length=100, blank=True, null=True)
    locationAddress = models.CharField(verbose_name="Address", max_length=200)
    
    def image(self):
        return mark_safe('<img src="/../../media/%s" width="70" />' % (self.profilePicture))
    
    image.allow_tags = True 

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)



class Trainee(models.Model):
    class Status(models.TextChoices):
        SELECT = "", "Select Status"
        PENDING = "Pending", "Pending"
        AWARDED = "Awarded", "Awarded"

    user = models.OneToOneField(User, verbose_name="User", related_name="trainees", on_delete=models.CASCADE)
    nid = models.CharField(verbose_name="National ID OR Passport", max_length=20, unique=True)
    git_account = models.CharField(verbose_name="Git Account Link", max_length=1000, unique=True)
    profilePicture = models.ImageField(
        verbose_name="Image", 
        upload_to="images/profile/", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        blank=True, null=True
    )
    phone1 = PhoneNumberField(verbose_name="Phone 1", blank=True)
    phone2 = PhoneNumberField(verbose_name="Phone 2", blank=True)
    cohort = models.OneToOneField(Cohort, verbose_name="Cohort belonging", related_name="cohorts", on_delete=models.CASCADE)
    stack = models.OneToOneField(Stack, verbose_name="Stack belonging", related_name="stacks", on_delete=models.CASCADE)
    locationAddress = models.CharField(verbose_name="Address", max_length=200)
    status = models.CharField(verbose_name="Status", choices=Status.choices, default=Status.SELECT, max_length=10)
    
    def image(self):
        return mark_safe('<img src="/../../media/%s" width="70" />' % (self.profilePicture))
    
    image.allow_tags = True 

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)



class ProgramManager(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="managers", on_delete=models.CASCADE)
    ssn = models.CharField(verbose_name="SSN", max_length=100, blank=True, null=True)
    profilePicture = models.ImageField(
        verbose_name="Image", 
        upload_to="images/profile/", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        blank=True, null=True
    )
    phone1 = PhoneNumberField(verbose_name="Phone 1", blank=True)
    phone2 = PhoneNumberField(verbose_name="Phone 2", blank=True)
    locationAddress = models.CharField(verbose_name="Address", max_length=200)
    
    def image(self):
        return mark_safe('<img src="/../../media/%s" width="70" />' % (self.profilePicture))
    
    image.allow_tags = True 

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)



class Company(models.Model):
    user = models.OneToOneField(User, verbose_name="User", related_name="companies", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Company Name", max_length=50, unique=True)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True, blank=False)
    fixed_phone = PhoneNumberField(verbose_name="Phone Number", blank=True)
    location = models.CharField(verbose_name="Location Address", max_length=200)
    logoFile = models.ImageField(
        verbose_name="Logo Image", 
        upload_to="images/profile/", 
        validators=[FileExtensionValidator(['png','jpg','jpeg'])],
        blank=True, null=True
    )
    
    def logo(self):
        return mark_safe('<img src="/../../media/%s" width="70" />' % (self.logoFile))
    
    logo.allow_tags = True 

    def __str__(self):
        return self.name