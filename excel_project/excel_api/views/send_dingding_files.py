import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from utils import mail_utils



class SendEmailView(APIView):



    def get(self,request):


        try:
            self.send_files()
            return Response({"msg": f"已发送邮件"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    def send_files(self):
        self.dictionary =  os.path.join(settings.BASE_DIR,'部门考勤数据')
        dept_emails = {
            "财务": "peter.mo@iss-gf.com",
            "采购": "peter.mo@iss-gf.com",
            "IT": "peter.mo@iss-gf.com",
            "海运": "peter.mo@iss-gf.com",
            "空运": "peter.mo@iss-gf.com",
            "商务": "peter.mo@iss-gf.com",
            "项目": "peter.mo@iss-gf.com",
            "宁波": "peter.mo@iss-gf.com",
            "深圳": "peter.mo@iss-gf.com"
        }

        for f in os.listdir(self.dictionary):
            for dept, email in dept_emails.items():
                if f.startswith(dept):
                    path = os.path.join(self.dictionary, f)
                    print(path)
                    if os.path.isfile(path):
                        print("yes")
                        mail_utils.send_email(email, path)
                    break