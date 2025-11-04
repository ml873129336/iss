from rest_framework import viewsets, filters
from ..models import Asset, Employee
from ..serializers import  EmployeeSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'employee_id']