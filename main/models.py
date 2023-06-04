from django.db import models
from django.core.validators import FileExtensionValidator

# from account.models import Trainer


class Cohort(models.Model):
    cohort_name = models.CharField(verbose_name="Cohort Name", max_length=100, unique=True)
    starting_date = models.DateField(verbose_name="When Start")
    ending_date = models.DateField(verbose_name="When End")
    def __str__(self):
        return self.cohort_name


class Stack(models.Model):
    name = models.CharField(verbose_name="Stack Name", max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    def __str__(self):
        return self.name


class Module(models.Model):
    stack = models.OneToOneField(Stack, verbose_name="Stack belonging", related_name="courses", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Course Name", max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    documentFiles = models.FileField(
        verbose_name="Document", 
        upload_to="document/course/", 
        validators=[FileExtensionValidator(['pdf','doc'])],
        blank=True, null=True
    )
    def __str__(self):
        return self.name

# class Team(models.Model):
# - lab = models.OneToOneField(Cohort, verbose_name="Cohort", related_name="labs", on_delete=models.CASCADE)
# - trainee (foreignKey)
# - name = models.CharField(verbose_name="Stack Name", max_length=100, unique=True)

# class Assignment(models.Model):
# - lab (foreignKey)
# - title = models.CharField(verbose_name="Stack Name", max_length=100, unique=True)
# - description
# - documentFile (upload [.pdf, .doc, .ppt])
# - submitionDate (datetime)

# class Report(models.Model):
# - assignment (foreignKey)
# - team (foreignkey)
# - description
# - documentFile (upload [.pdf, .doc, .ppt])
# - dateCreated (datetime)
# - status (option: #unread, #read)

# class Feedback(models.Model):
# - assignment (oneToOne)
# - description
# - documentFile (upload [.png, .jpg, .pdf, .doc, .ppt])
# - createdDate(datetime)

# #RecruitmentAnnouncement
# - cohort (oneToOne)
# - title
# - description
# - start_date (date)
# - end_date (date)
# - createDated (date)

# #TrainingApplication
# - cohort (foreignKey)
# - stack = models.OneToOneField(Stack, verbose_name="Stack belonging", related_name="stacks", on_delete=models.CASCADE)
# - first_name
# - last_name
# - email
# - gender
# - phone
# - location address
# - cv ( #upload_document)
# - createdDate (date)

# #Requitment
# - user (foreignKey -> company)
# - talent (foreignKey -> trainee[awarded])
# - status ( #confirmed: hided)
# - dateCreated
