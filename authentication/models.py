from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
from django.contrib.auth.models import AbstractUser

from .user_manager import CustomUserManager

# Custom User Model that is Only Unique to this project.


class User(AbstractUser):

    # remove the username field
    username = None

    # add the phone_number field as the new unique identifier
    phone_number = models.CharField(
        validators=[RegexValidator(
            r'^07\d{8}$', "Phone number must be exactly 10 digits and must be a rwandan Number.")],
        max_length=10,
        unique=True,
        null=False,
        blank=False,
        help_text="Phone number must be exactly 10 digits and start with '07'"
    )
    # add the email and national_id fields
    email = models.EmailField(unique=True, null=False,
                              blank=False)

    # set the phone_number field as the USERNAME_FIELD
    USERNAME_FIELD = 'phone_number'

    # make the email and national_id fields required
    REQUIRED_FIELDS = ['email']
    # set the CustomUserManager as the default manager
    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.phone_number}=>{self.email}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    bio = models.TextField()
    image = models.ImageField(default="default.jpg",
                              upload_to=f"media/profiles/")
    dob = models.DateField()
    social_instagram = models.CharField(max_length=200, blank=True, null=True)
    social_twitter = models.CharField(max_length=200, blank=True, null=True)
    social_linkedin = models.CharField(max_length=200, blank=True, null=True)
    social_website = models.CharField(max_length=200, blank=True, null=True)
# Creating the Address Model


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="address",
                             on_delete=models.CASCADE)
    province = models.CharField(max_length=250, null=True)
    district = models.CharField(max_length=250, null=True)
    sector = models.CharField(max_length=250, null=True)
    street_name = models.CharField(max_length=250, null=True)

    def __str__(self):
        return "{}@{}".format(self.sector, self.street_name)
