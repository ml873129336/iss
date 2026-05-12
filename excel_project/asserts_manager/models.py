from django.utils import timezone
from django.db import models
from rest_framework import serializers
import os

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_departments')

    def __str__(self):
        return self.name

class Employee(models.Model):
    CITY_CHOICES = [
        ('SHA', 'Shanghai'),
        ('NGB', 'Ningbo'),
        ('SZX', 'Shenzhen'),
    ]
    name = models.CharField(max_length=100)
    mail = models.CharField(max_length=100,default='')
    city = models.CharField(max_length=10, choices=CITY_CHOICES,default="")
    employee_id = models.CharField(max_length=10,default=999999)
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    reporting_line = models.CharField(max_length=100,default=None)
    onboard_date = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.name:
            # 始终根据最新的 name 生成邮箱
            self.mail = self.name.strip().replace(' ', '.').lower() + '@iss-gf.com'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



def asset_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    hostname = instance.hostname or "unknown"
    return os.path.join("autopilot_csv/assets/", f"{hostname}{ext}")

class Asset(models.Model):
    STATUS_CHOICES = [
        ('in_use', '在用'),
        ('idle', '闲置'),
        ('repair', '维修中'),
        ('scrapped', '报废'),
    ]

    CATEGORY_CHOICES = [
        ('laptop', '笔记本')
    ]

    CATEGORY_CODE = {
        'laptop': 'wna',
        'desktop': 'wda',
        # 可以继续扩展其他类别
    }

    CITY_CHOICES = [
        ('SHA', 'Shanghai'),
        ('NGB', 'Ningbo'),
        ('SZX', 'Shenzhen'),
    ]
    DESCRIPTION_CHOICES = [
        ('thinkpad14','Thinkpad丨 ThinkBook 14丨 I5-1135G7 丨512-SSD 丨 14')

    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='laptop')
    description = models.CharField(max_length=20, choices=DESCRIPTION_CHOICES, default='thinkpad14')
    user = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    purchase_date = models.DateField(default=timezone.now)
    price = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    remark = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=10, choices=CITY_CHOICES, default='SHA')
    hostname = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(upload_to=asset_upload_path,null=True,blank=True)

    def save(self, *args, **kwargs):
        # 自动根据 user 更新 city
        if self.user and self.user.city:
            self.city = self.user.city

        if not self.hostname:
            prefix = 'cn'
            city_code = self.city.lower()
            category_code = self.CATEGORY_CODE.get(self.category, 'wna')

            # 获取同城市同类别的最新编号
            last_asset = Asset.objects.filter(city=self.city, category=self.category).order_by('-id').first()
            if last_asset and last_asset.hostname:
                try:
                    last_number = int(last_asset.hostname[-5:])
                except:
                    last_number = 0
            else:
                last_number = 0

            new_number = str(last_number + 1).zfill(5)
            self.hostname = f"{prefix}{city_code}{category_code}{new_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
