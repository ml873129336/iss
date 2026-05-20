from django.urls import path
from django.urls import path
from .views import ExcelUploadView,Iss_Fin_solve_excel,SendEmailView,Iss_Fin1_solve_excel,Iss_Fin2_solve_excel

urlpatterns = [
    path("upload-excel/", ExcelUploadView.as_view()),
    path("send_files/", SendEmailView.as_view()),
    path("iss_fin/", Iss_Fin_solve_excel.as_view()),
    path("iss_fin1/", Iss_Fin1_solve_excel.as_view()),
    path("iss_fin2/", Iss_Fin2_solve_excel.as_view()),
]