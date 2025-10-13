from django.urls import path
from django.urls import path
from .views import ExcelUploadView,Iss_Fin_solve_excel

urlpatterns = [
    path("upload-excel/", ExcelUploadView.as_view()),
    path("iss_fin/", Iss_Fin_solve_excel.as_view()),
]