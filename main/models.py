from django.db import models


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