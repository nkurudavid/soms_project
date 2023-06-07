from django.core.validators import FileExtensionValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from main.models import Cohort, Stack

# Create your models here.
class Application(models.Model):
    class Gender(models.TextChoices):
        SELECT = "", "Select Gender"
        MALE = "Male", "Male"
        FEMALE = "Female", "Female"

    class Education(models.TextChoices):
        SELECT = "", "Select Education Level"
        BACHELORS= "Bachelors Degree", "Bachelors Degree"
        ADVANCED_DIPLOMA= "Advanced diploma", "Advanced diploma"
        HIGH_SCHOOL= "High School", "High School"

    cohort = models.ForeignKey(Cohort, verbose_name="Cohort to Join", related_name="applicants", on_delete=models.PROTECT)
    stack = models.ForeignKey(Stack, verbose_name="Stack to Join", related_name="applicants", on_delete=models.PROTECT)
    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True, blank=False)
    gender = models.CharField(verbose_name="Gender", choices=Gender.choices, default=Gender.SELECT, max_length=10)
    phone1 = PhoneNumberField(verbose_name="Phone 1", blank=True)
    phone2 = PhoneNumberField(verbose_name="Phone 2", blank=True)
    locationAddress = models.CharField(verbose_name="Address", max_length=200)
    githubLink = models.URLField(max_length=255, blank=False, null=False)
    educationLevel = models.CharField(verbose_name="Education Level", choices=Education.choices, default=Education.SELECT, max_length=30)
    cv_file = models.FileField(
        verbose_name="CV Document",
        upload_to="document/applicants/",
        validators=[FileExtensionValidator(['pdf','doc'])],
        blank=True, null=True
    )
    more = models.TextField(verbose_name="More Information", blank=True)
    status = models.BooleanField(verbose_name="Is Application Confirmed ?", default=False)
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)