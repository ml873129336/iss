from django.db import models
from rest_framework import serializers

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10,default=999999)
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    reporting_line = models.CharField(max_length=100)
    onboard_date = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS_CHOICES = [
        ('in_use', '在用'),
        ('idle', '闲置'),
        ('repair', '维修中'),
        ('scrapped', '报废'),
    ]

    CATEGORY_CHOICES = [
        ('laptop','笔记本')
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='laptop')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    purchase_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    remark = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)