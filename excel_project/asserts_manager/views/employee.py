from rest_framework.response import Response
from rest_framework import viewsets, filters,status
from rest_framework.decorators import action
import pandas as pd
from ..models import Asset, Employee,Department
from ..serializers import  EmployeeSerializer
from utils.excel_utils import read_excel_to_df
from utils.mail_utils import send_email

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'employee_id']

    def create(self, request, *args, **kwargs):
        """
        兼容两种情况：
        1️⃣ 普通 JSON 请求（新增单个员工）
        2️⃣ 上传 Excel 文件（批量导入）
        """

        # 🟢 情况 1：上传文件（Excel 导入）


        # 🟢 情况 2：普通 JSON 创建单个员工\
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("验证失败：", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            print("后端异常：", traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def send_onboarding_email(self, request, pk=None):
        employee = self.get_object()
        if not employee.mail:
            return Response({"detail": "员工邮箱未设置"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subject = "新员工入职邮件"
            display_name = employee.name +" (ISS CN)"
            HTML_BODY = f"""\
            <html>
              <body>
                <p>Dear {employee.name},<br><br>
                   Good Afternoon!<br><br>
                   ISSGF系统(邮箱) 和 NAS 账号现已开通，详情如下, 请另外做好记录或保存！；<br><br>
                   <strong>ISS-GF系统（邮箱）：</strong><br>
                   Display name: <strong>{display_name}</strong><br><br>
                   Username: <strong>{employee.mail}</strong><br><br>
                   Password: <strong>Iss202303!</strong><br><br>
                   <em>*这为原始密码，短期内请勿修改，如需修改，请务必牢记</em><br>
                   <em>*若在家里电脑中收发邮件，请使用“网页版”,网址为：outlook.office.com</em>
                </p>
              </body>
            </html>
            """

            send_email(employee.mail,subject,HTML_BODY,"html",attachment="")

            return Response({"detail": "入职邮件已发送"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '未上传文件'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({'error': f'Excel 读取失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        required_columns = [
            'First Name', 'Last Name', 'Title', 'Department',
            'Reports TO', 'City', 'New E-Mail ID'
        ]
        for col in required_columns:
            if col not in df.columns:
                return Response({'error': f'缺少列: {col}'}, status=400)

        created, updated, errors = 0, 0, []

        for idx, row in df.iterrows():
            try:
                first = str(row.get('First Name', '')).strip()
                last = str(row.get('Last Name', '')).strip()
                if not first and not last:
                    errors.append({'row': idx, 'error': '缺少姓名'})
                    continue

                name = f"{first} {last}".strip()

                # 部门
                dept_name = str(row.get('Department', '')).strip()
                dept = None
                if dept_name:
                    dept, _ = Department.objects.get_or_create(name=dept_name)

                # 城市
                CITY_MAP = {
                    'Shanghai': 'SHA',
                    'Ningbo': 'NGB',
                    'Shenzhen': 'SZX',
                }

                city_raw = str(row.get('City', '')).strip()
                city_value = CITY_MAP.get(city_raw, 'SHA')

                email_from_excel = str(row.get('New E-Mail ID', '')).strip()

                emp = Employee.objects.filter(name=name).first()

                if emp:
                    # 更新
                    emp.position = row.get('Title', emp.position)
                    emp.department = dept
                    emp.city = city_value
                    emp.reporting_line = row.get('Reports TO', emp.reporting_line)
                    emp.mail = email_from_excel or emp.mail
                    emp.save()
                    updated += 1

                else:
                    # 自动生成 employee_id
                    new_id = Employee.objects.count() + 1
                    new_id = f"{new_id:06d}"

                    Employee.objects.create(
                        name=name,
                        employee_id=new_id,
                        position=row.get('Title', ''),
                        department=dept,
                        city=city_value,
                        reporting_line=row.get('Reports TO', ''),
                        mail=email_from_excel,
                        onboard_date=""
                    )
                    created += 1

            except Exception as e:
                errors.append({'row': idx, 'error': str(e)})

        return Response({
            'created': created,
            'updated': updated,
            'errors': errors,
        })

