from django.db import models
from rest_framework import serializers

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10,default=999999)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    reporting_line = models.CharField(max_length=100)
    onboard_date = models.CharField(max_length=100)

    def __str__(self):
        return self.name

