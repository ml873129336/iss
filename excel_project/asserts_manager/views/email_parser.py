import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils import mail_utils
from datetime import datetime

"""解析上传的邮件"""
class EmailParseView(APIView):
    def post(self, request):

        text = request.data.get('email_body', '')

        created =mail_utils.record_new_employee_data(text)

        return Response({'created': created}, status=201)

    def get(self,request):

        body_list = mail_utils.check_email("Onboarding")

        created=""
        for body in body_list:

            created = mail_utils.record_new_employee_data(body['body'])

        return Response({'created': created}, status=201)

"""解析直接从邮箱获取的邮件"""

# class GetEmailParse(APIView):
#     def get(self,request):
#         body_list = mail_utils.check_email()
#
#         for body in body_list:
#             created = mail_utils.record_new_employee_data(body)
#
#         return Response({'created': created}, status=201)