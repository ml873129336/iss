from rest_framework import viewsets, filters
from ..models import Asset
from ..serializers import AssetSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().order_by('-updated_at')
    serializer_class = AssetSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'serial_number', 'user__name', 'department__name', 'category__name']
    ordering_fields = ['updated_at', 'name']

    # 额外按状态/部门/员工筛选
    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        department_id = self.request.query_params.get('department')
        user_id = self.request.query_params.get('user')
        if status:
            queryset = queryset.filter(status=status)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


