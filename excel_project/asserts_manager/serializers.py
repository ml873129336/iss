from rest_framework import serializers
from .models import Asset,Department,Employee

from datetime import date

class EmployeeSerializer(serializers.ModelSerializer):


    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("员工姓名不能为空。")

        if not self.instance and Employee.objects.filter(name=value).exists():
            raise serializers.ValidationError(value+" 该名字已存在")

        return value

    class Meta:
        model = Employee
        fields = '__all__'

    # 字段校验：onboard_date_before 不应早于今天
    # def validate_onboard_date(self, value):
    #     if value < date.today():
    #         raise serializers.ValidationError("入职日期不能早于今天。")
    #     return value

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']





class AssetSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    description_display = serializers.CharField(source='get_description_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    user = EmployeeSerializer(read_only=True)  # 嵌套显示
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='user',
        write_only=True
    )



    class Meta:
        model = Asset
        fields = '__all__'

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]  # 🔹 取真实文件名
        return None