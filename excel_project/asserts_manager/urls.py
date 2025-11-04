
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet,EmailParseView,EmployeeViewSet,AssetViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'departments', DepartmentViewSet)


urlpatterns = [
    path('assert_manager/', include(router.urls)),
    path("parse_email/", EmailParseView.as_view()),
    # path("get_email/", GetEmailParse.as_view()),

]