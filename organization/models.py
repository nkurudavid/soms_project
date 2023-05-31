from django.conf import settings
from django.db import models



TRAINEE_GENDER = (
    ("M", "Male"),
    ("F", "Female"),
)

# Solvit/ Enterprise models


class Cohort(models.Model):
    organization = models.ForeignKey(
        "organization", related_name="cohorts", on_delete=models.CASCADE)
    cohort_name = models.CharField(max_length=255)
    cohort_counter = models.IntegerField()
    starting_date = models.DateTimeField()
    ending_date = models.DateTimeField()

    def __str__(self) -> str:
        return self.cohort_name+f"({str(self.cohort_counter)})"


# Keeps track of all stacks of a given cohorts


class Stack(models.Model):
    organization = models.ForeignKey(
        "Organization", related_name="stacks", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    starting_date = models.DateTimeField()

    def __str__(self) -> str:
        return self.name
# Keeps track of a given organization


class Organization(models.Model):
    name = models.CharField(max_length=244)
    description = models.TextField()
    website = models.URLField()
    country = models.CharField(max_length=244)
    province = models.CharField(max_length=244)
    district = models.CharField(max_length=244)
    sector = models.CharField(max_length=244)
    address = models.CharField(max_length=244)
    logo = models.ImageField(default="default.jpg",
                             upload_to=f"media/organization")
    phone_number = models.CharField(max_length=244)

    def __str__(self):
        return f"{self.name}@{self.phone_number}"


class OrganizationPosition(models.Model):
    name = models.CharField(max_length=244)
    since = models.DateField()
# -----------------------------------------------------
# Peopler Who are Training in the cohort


class TrainerPosition(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="position", on_delete=models.CASCADE)
    position = models.ForeignKey(
        OrganizationPosition, on_delete=models.CASCADE
    )


class Trainer(models.Model):
    organization = models.ForeignKey(
        Organization, related_name="trainers", on_delete=models.CASCADE)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="trainer", on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=2, choices=TRAINEE_GENDER, blank=False, null=False)
    stack = models.ForeignKey(
        Stack, on_delete=models.CASCADE, blank=True, null=True)
    resume = models.FileField(upload_to="media/trainer/resume")
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    dob = models.DateField()

# -----------------------------------------------------
# people who are being trained by trainee


class Trainee(models.Model):
    organization = models.ForeignKey(
        Organization, related_name="trainee", on_delete=models.CASCADE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="trainee", on_delete=models.CASCADE)
    gender = models.CharField(
        max_length=2, choices=TRAINEE_GENDER, blank=False, null=False)
    cohort = models.ForeignKey(
        Cohort, on_delete=models.CASCADE, blank=True, null=True)
    stack = models.ForeignKey(
        Stack, on_delete=models.CASCADE, blank=True, null=True)
    resume = models.FileField(upload_to="media/trainee/resume")
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    dob = models.DateField()


# Keep track of those who were outsourced
class Outsource(models.Model):
    organization = models.ForeignKey(
        Organization, related_name="outsource", on_delete=models.CASCADE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="outsource", on_delete=models.CASCADE)
    outsource_to = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)
