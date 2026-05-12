
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet,EmailParseView,EmployeeViewSet,AssetViewSet,it_payment_colipu,payment_preview,payment_download,payment_send_email

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'departments', DepartmentViewSet)


urlpatterns = [
    path('assert_manager/', include(router.urls)),
    path("parse_email/", EmailParseView.as_view()),
    path("it_payment_colipu/", it_payment_colipu),
    path("paymen_download/", payment_download),
    path("payment_preview/", payment_preview),
    path("payment_send_email/",payment_send_email)
]