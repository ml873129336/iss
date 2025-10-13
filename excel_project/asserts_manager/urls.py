from django.urls import path
from django.urls import path
from .views import EmailParseView


urlpatterns = [
    path("parse_email/", EmailParseView.as_view()),
    # path("get_email/", GetEmailParse.as_view()),
]