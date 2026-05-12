from rest_framework import viewsets, filters,status
from ..models import Asset,Employee
from ..serializers import AssetSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import traceback
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.dateparse import parse_date
from datetime import datetime


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().order_by('city',"user")
    serializer_class = AssetSerializer
    parser_classes = (MultiPartParser, FormParser)

    from rest_framework.exceptions import ValidationError
    from django.core.exceptions import ObjectDoesNotExist
    from django.utils.dateparse import parse_date
    import traceback

    @action(detail=False, methods=['post'])
    def upload_excel(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "请上传 excel 文件"}, status=400)

        # 读取 Excel
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({"error": f"Excel 解析失败: {str(e)}"}, status=400)

        # 必须包含哪些列
        required_cols = [
            "Description", "Purchase date", "Site", "User",
            "Remark", "S/N No.", "ID Name", "Item"
        ]

        for col in required_cols:
            if col not in df.columns:
                return Response({"error": f"缺少列: {col}"}, status=400)

        created = []
        errors = []

        for idx, row in df.iterrows():
            row_number = idx + 2  # Excel 行号（排除表头）

            try:
                # ------ 字段解析转换 -------

                # Description 解析
                desc_value = row["Description"]
                description = "thinkpad14" if "Thinkpad" in desc_value else "thinkpad14"

                # 日期解析
                raw_date = row["Purchase date"]
                if isinstance(raw_date, datetime):
                    purchase_date = raw_date.date()
                else:
                    purchase_date = parse_date(str(raw_date)) or timezone.now().date()

                # 站点解析 SZX-Shenzhen → SZX
                site = str(row["Site"])
                city_code = site.split("-")[0]
                if city_code not in dict(Asset.CITY_CHOICES):
                    city_code = "SHA"

                # 查找使用人
                username = str(row["User"]).strip()
                user_obj = Employee.objects.filter(name=username).first()
                if not user_obj:
                    raise ValidationError({"user": [f"未找到用户: {username}"]})

                # SN 校验
                serial = str(row["S/N No."]).strip()
                if Asset.objects.filter(serial_number=serial).exists():
                    raise ValidationError({"serial_number": [f"S/N 重复: {serial}"]})

                # ------ Serializer 验证 + 创建 -------
                serializer = AssetSerializer(data={
                    "category": "laptop",
                    "description": description,
                    "serial_number": serial,
                    "purchase_date": purchase_date,
                    "city": city_code,
                    "user": user_obj.id,
                    "remark": row.get("Remark", ""),
                    "hostname": row.get("ID Name", "")
                })

                serializer.is_valid(raise_exception=True)
                serializer.save()

                created.append(serial)

            except ValidationError as ve:
                # DRF 验证错误（字段错误非常清晰）
                errors.append({
                    "row": row_number,
                    "error": ve.detail
                })

            except Exception as e:
                # 其他错误
                errors.append({
                    "row": row_number,
                    "error": str(e),
                    "trace": traceback.format_exc()
                })

        return Response({
            "created": created,
            "errors": errors
        })

    def create(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                print("验证失败：", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:

            print("后端异常：", traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def update(self, request, *args, **kwargs):
        """
        更新资产（PUT）
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

            if not serializer.is_valid():
                print("🟥 更新验证失败：", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            self.perform_update(serializer)
            print("🟩 更新成功：", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print("🟥 后端更新异常：", traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def destroy(self, request, *args, **kwargs):
        """
        删除资产
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            print(f"🟩 删除成功：ID={instance.id}")
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            print("🟥 删除异常：", traceback.format_exc())
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)