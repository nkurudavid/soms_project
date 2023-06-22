from django.db import models
from django.utils.safestring import mark_safe
from django.core.validators import FileExtensionValidator



class Company(models.Model):
    name = models.CharField(verbose_name="Company Name", max_length=50, unique=True)
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


class Cohort(models.Model):
    cohort_name = models.CharField(verbose_name="Cohort Name", max_length=100, unique=True)
    starting_date = models.DateField(verbose_name="When Start")
    ending_date = models.DateField(verbose_name="When End")
    status = models.BooleanField(verbose_name="Is Completed", default=False)
    def __str__(self):
        return self.cohort_name


class Cohort_schedule(models.Model):
    class Schedule(models.TextChoices):
        SELECT = "", "Select Schedule"
        APPLICATION = "Application", "Application"
        INTERVIEW = "Interview", "Interview"
        GRADUATION = "Graduation", "Graduation"

    cohort = models.ForeignKey(Cohort, verbose_name="Cohort Scheduled", related_name="schedules", on_delete=models.CASCADE)
    schedule_name = models.CharField(verbose_name="Schedule Name", choices=Schedule.choices, default=Schedule.SELECT, max_length=12)
    start_period = models.DateTimeField()
    end_period = models.DateTimeField()

    def __str__(self):
       return self.schedule_name


class Stack(models.Model):
    name = models.CharField(verbose_name="Stack Name", max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    def __str__(self):
        return self.name


class Module(models.Model):
    stack = models.ForeignKey(Stack, verbose_name="Stack belonging", related_name="modules", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="Module Name", max_length=100, unique=True)
    description = models.TextField(verbose_name="Description", blank=True)
    documentFiles = models.FileField(
        verbose_name="Document", 
        upload_to="document/course", 
        validators=[FileExtensionValidator(['pdf','doc','docx','ppt'])],
        blank=True, null=True
    )
    def __str__(self):
        return self.name


class Group(models.Model):
    cohort = models.ForeignKey(Cohort, verbose_name="Cohort belonging", related_name="groups", on_delete=models.CASCADE)
    stack = models.ForeignKey(Stack, verbose_name="Stack belonging", related_name="groups", on_delete=models.CASCADE)
    group_name = models.CharField(verbose_name="Group Name", max_length=100)
    def __str__(self):
        return "{} {}".format(self.group_name, self.stack)


class Assignment(models.Model):
    cohort = models.ForeignKey(Cohort, verbose_name="Cohort belonging", related_name="assignments", on_delete=models.CASCADE)
    stack = models.ForeignKey(Stack, verbose_name="Stack belonging", related_name="assignments", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="Assignment Title", max_length=100)
    description = models.TextField(verbose_name="Description", blank=True)
    documentFiles = models.FileField(
        verbose_name="Document", 
        upload_to="document/course/assignment", 
        validators=[FileExtensionValidator(['pdf','doc','docx','ppt'])],
        blank=True, null=True
    )
    status = models.BooleanField(verbose_name="Is Marked", default=False)
    startDate = models.DateTimeField(blank=True, null=True)
    dueDate = models.DateTimeField(blank=True, null=True)
    createdDate = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title


class AssignmentReport(models.Model):
    group = models.ForeignKey(Group, verbose_name="Submitting Group", related_name="reports", on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, verbose_name="Assignment", related_name="reports", on_delete=models.CASCADE)
    description = models.TextField(verbose_name="Description", blank=True)
    documentFiles = models.FileField(
        verbose_name="Document", 
        upload_to="document/course/assignment/report", 
        validators=[FileExtensionValidator(['pdf','doc','docx','ppt'])],
        blank=True, null=True
    )
    status = models.BooleanField(verbose_name="Is Received", default=False)
    createdDate = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.group.group_name


class Feedback(models.Model):
    report = models.OneToOneField(AssignmentReport, verbose_name="Assignment Report", related_name="feedbacks", on_delete=models.CASCADE)
    grade = models.CharField(verbose_name="Assignment Grade", max_length=100, unique=True)
    comment = models.TextField(verbose_name="Comment", blank=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.comment
