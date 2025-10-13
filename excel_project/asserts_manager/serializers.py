from rest_framework import serializers
from .models import Employee
from datetime import date

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("员工姓名不能为空。")

        if not self.instance and Employee.objects.filter(name=value).exists():
            raise serializers.ValidationError(value+" 该名字已存在")

        return value

    # 字段校验：onboard_date_before 不应早于今天
    # def validate_onboard_date(self, value):
    #     if value < date.today():
    #         raise serializers.ValidationError("入职日期不能早于今天。")
    #     return value