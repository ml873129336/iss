from django.shortcuts import render
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
import pandas as pd
import re
import traceback
import os
import shutil
from utils import mail_utils

from django.conf import settings


class ExcelUploadView(APIView):
    parser_classes = [MultiPartParser]

    def get(self,request):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "未上传文件"}, status=400)

        if file.name.startswith("请假"):
            df = pd.read_excel(file)
            self.depts = df["部门"].dropna().unique().tolist()

        elif "考勤" in file.name:
            df = pd.read_excel(file, skiprows=2,
                               usecols=['姓名', '部门', '日期', '上班1打卡时间', '上班1打卡结果', '下班1打卡时间', '下班1打卡结果'],
                               sheet_name="每日统计")
            self.depts = df["部门"].dropna().unique().tolist()
        return Response(self.depts)



    def post(self, request, format=None, ):

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "未上传文件"}, status=400)

        try:
            print(file.name)

            # result =1
            if file.name.startswith("请假"):
                df = pd.read_excel(file)
                df_clean = df.fillna("")
                df_clean = df_clean[df_clean['审批状态'] != '终止']
                df_result = self.solve_leave(df_clean)
                title="请假记录"

            elif file.name.startswith("艾斯捷国际运输(上海)有限公司"):
                print(1)
                df = pd.read_excel(file,skiprows=2,usecols=['姓名', '部门','日期','上班1打卡时间','上班1打卡结果','下班1打卡时间','下班1打卡结果'],sheet_name="每日统计")
                df = df.drop(index=0).reset_index(drop=True)
                df_clean = df.fillna("")
                print(df_clean)
                df_result = self.solve_attendence(df_clean)
                title= "缺卡记录"

            else:
                df = pd.read_excel(file)
                df_clean = df.fillna("")
                df_result = df_clean.to_dict(orient="records")
                title = "其他"

            # df_sorted = df_result.sort_values(by=['创建人部门', '创建人'])
            return Response({"data": df_result,"title":title,"code":200}, status=200)
        except Exception as e:
            print(traceback.print_exc())
            return Response({"error": str(e)}, status=500)

    def solve_attendence(self,df):
        status = ['正常', '外勤','','管理员莫良-Peter Mo改为正常','请假','外出']
        filter_user = ["杨剑书-Edward Yang","周诗炯-George Zhou","方晨曦-Fang Sean","张明秋","储青利-Liz Chu","罗健-Ken Luo"]
        df_filter = df[
            (~df['上班1打卡结果'].isin(status)) |
            (~df['下班1打卡结果'].isin(status))  &
            (~df['姓名'].isin(filter_user))
            ]
        self.split_dep_tofile(df_filter)

        return df_filter.to_dict(orient="records")


    def solve_leave(self,df_clean):
        columns = ["创建人部门", "创建人", "开始时间", "请假类型", "时长"]
        result = df_clean[columns]
        result[['时长', '单位']] = result['时长'].apply(lambda x: pd.Series(self.split_value_unit(x)))
        pivot_day = result[result['单位'] == '天'].pivot_table(index='创建人', columns='请假类型', values='时长', aggfunc='sum',
                                                            fill_value=0)
        pivot_hour = result[result['单位'] == '小时'].pivot_table(index='创建人', columns='请假类型', values='时长', aggfunc='sum',
                                                              fill_value=0)
        pivot_day.reset_index(inplace=True)
        pivot_day["总结"] = pivot_day.apply(lambda row: self.sum_date(row, "天"), axis=1)
        # print(pivot_day)
        pivot_hour.reset_index(inplace=True)
        pivot_hour["总结"] = pivot_hour.apply(lambda row: self.sum_date(row, "小时"), axis=1)

        # print(pivot_hour)
        # df_result = result.to_dict(orient="records")  # 处理前5行作为示例
        df_merged = pd.merge(pivot_day[["创建人", "总结"]], pivot_hour[["创建人", "总结"]], on="创建人", how='left').fillna("")
        df_merged['总结'] = df_merged['总结_x'] + '\n' + df_merged['总结_y']
        df_merged.drop(columns=['总结_x', '总结_y'], inplace=True)
        # print(df_merged)
        df_final = pd.merge(df_clean[columns], df_merged, on="创建人", how="left")
        df_final = df_final.sort_values(by=['创建人部门', '创建人'])
        df_result = df_final.to_dict(orient="records")
        return df_result


    def split_dep_tofile(self, df):
        output_dir = '部门考勤数据'
        if os.path.exists(output_dir):
            # 删除目录下的所有文件和子目录，但保留该目录本身
            for item in os.listdir(output_dir):
                item_path = os.path.join(output_dir, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # 删除文件或软链接
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # 删除子目录
                except Exception as e:
                    print(f"删除失败: {item_path}, 原因: {e}")
        else:
            os.makedirs(output_dir, exist_ok=True)
            print(f"已创建目录: {output_dir}")


        # 获取所有唯一的部门列表
        departments = df['部门'].unique()

        # 遍历每个部门，分别保存为独立的Excel文件
        for department in departments:
            # 筛选出当前部门的数据
            department_df = df[df['部门'] == department]

            # 清理文件名中的特殊字符
            clean_department_name = ''.join(c for c in department if c not in r'\/:*?"<>|')
            file_name = f'{clean_department_name}_异常考勤数据.xlsx'
            file_path = os.path.join(output_dir, file_name)

            # 保存为Excel文件
            department_df.to_excel(file_path, index=False, engine='openpyxl')
            print(f'已生成: {file_path}')

        dir = os.path.join(settings.BASE_DIR,'部门考勤数据')
        print(f'\n所有部门数据已导出到目录: {dir}')
        # self.send_file_to_department(dir)

    def clear_files(self,folder_path):
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isfile(item_path):
                os.remove(item_path)





    def sum_date(self,row,unit):
        sum = []
        for col in row.index:
            if col == "创建人":
                continue
            val = row[col]
            if val > 0:
                sum.append(f"{col} {val}{unit}")
        if sum:
            # print(f"{row['创建人']}请了" + "，".join(sum))
            return f"{row['创建人']}请了" + "，".join(sum)
        else:
            # print(f"{row['创建人']}无请假")
            return f"{row['创建人']}无请假"


    def split_value_unit(self,x):
        match = re.match(r'([\d.]+)(小时|天)', x)
        if match:
            return float(match.group(1)), match.group(2)
        return 0, ''


