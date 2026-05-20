import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import email
import re
from datetime import datetime
from django.conf import settings
from email.header import decode_header, make_header
from asserts_manager.serializers import EmployeeSerializer
from asserts_manager.models import Department

import os

IMAP_SERVER = "imap.163.com"
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
EMAIL_ACCOUNT = "issemail@163.com"
PASSWORD = "CFeZ4mrMp8j4QZfC"
FOLDER = "收件箱"


"""解析邮件正文"""
def parse_email_body(msg,attachment):
    base_path = os.path.join(settings.MEDIA_ROOT, "attachments")
    today_str = datetime.now().strftime("%Y%m%d")
    save_path = os.path.join(base_path, today_str)

    result = {"subject": "", "body": "", "attachments": []}
    body=""
    #正文分析
    if not attachment:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    charset = part.get_content_charset() or 'utf-8'
                    result["body"] += part.get_payload(decode=True).decode(charset, errors='ignore')

        else:
            charset = msg.get_content_charset() or 'utf-8'
            result["body"] += msg.get_payload(decode=True).decode(charset, errors='ignore')

        return result
    #保存附件
    else:
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    # 解决中文乱码
                    filename = email.header.decode_header(filename)[0][0]
                    if isinstance(filename, bytes):
                        filename = filename.decode(errors="ignore")

                    os.makedirs(save_path, exist_ok=True)
                    filepath = os.path.join(save_path, filename)

                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))

                    file_path = f"{settings.MEDIA_URL}attachments/{filename}"

                    result["attachments"].append(file_path)

        return result["attachments"]

"""将数据存入数据库"""


# 连接收件服务器
def connet_email():
    # 连接邮箱
    imaplib.Commands['ID'] = ('AUTH')
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    typ, data =mail.login(EMAIL_ACCOUNT, PASSWORD)
    if typ == 'OK':
        print("✅ 邮箱登录成功")
    else:
        print("❌ 邮箱登录失败:", data)
    args = ("name", "issemail", "contact", EMAIL_ACCOUNT, "version", "1.0.0", "vendor", "myclient")
    mail._simple_command('ID', '("' + '" "'.join(args) + '")')

    # 选取inbox
    mail.select("INBOX")


    return mail

"""连接邮箱 并获取所有未读且关键字有"Onboarding"的邮件"""
def check_email(keyword):

    body_list = []
    try:
        mail = connet_email()
        status, messages = mail.search(None, "UNSEEN")


        if status == "OK":
            mail_ids = messages[0].split()  # 拆分成单个邮件编号
            count = len(mail_ids)  # 邮件数量
            print(f"📬 邮箱中共有 {count} 封邮件")
        else:
            print("❌ 搜索失败")

        # 遍历邮件
        for num in messages[0].split():
            #获取邮件数据

            msg_id = num.decode()
            status,data = mail.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                continue

            # 把原始字节数据解析成一个 EmailMessage 或 Message 对象。
            msg = email.message_from_bytes(data[0][1])
            #获取邮件标题
            subject = email.header.decode_header(msg.get("Subject"))[0][0]


            if isinstance(subject, bytes):
                subject = subject = str(make_header(decode_header(msg.get("Subject"))))

            print(subject)
            #如果邮件标题里还有关键字，提取其中内容加入列表
            if keyword.lower() in subject.lower() :

                body = parse_email_body(msg,attachment=False)

                body_list.append(body)
            if keyword.lower() in subject.lower() and keyword =="INV":
                files = parse_email_body(msg,attachment=True)
                body_list.append(files)


        mail.logout()

    except Exception as e:
        print(f"邮件处理出错: {e}")

    return body_list

import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os


def send_email(
    to,
    subject,
    body,
    body_type="plain",
    attachment=None,
    attachments=None,
    inline_image=None
):
    try:
        print("📨 开始构建邮件")

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ACCOUNT
        msg["To"] = to

        msg.attach(MIMEText(body, body_type, "utf-8"))

        # 单附件（路径）
        if attachment and os.path.exists(attachment):
            print("📎 添加本地附件")
            with open(attachment, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment)}"'
            msg.attach(part)

        # 多附件（bytes）
        if attachments:
            for filename, file_bytes in attachments:
                print(f"📎 添加附件: {filename}, 大小: {len(file_bytes)} bytes")
                part = MIMEApplication(file_bytes, Name=filename)
                part["Content-Disposition"] = f'attachment; filename="{filename}"'
                msg.attach(part)

        # 内嵌图片
        if inline_image:
            print("🖼️ 添加内嵌图片")
            cid, img_bytes = inline_image
            img = MIMEImage(img_bytes)
            img.add_header("Content-ID", f"<{cid}>")
            msg.attach(img)

        print("🔌 连接 SMTP 服务器...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            print("✅ SMTP连接成功")

            server.login(EMAIL_ACCOUNT, PASSWORD)
            print("🔑 登录成功")

            server.send_message(msg)
            print("✅ 邮件已发送（send_message 完成）")

        return True

    except (smtplib.SMTPException, socket.timeout, ConnectionResetError) as e:
        print("❌ 邮件发送失败:", e)
        raise e

# def send_email(to,subject,body,type,attachment):
#
#     msg = MIMEMultipart()
#     msg["Subject"] = subject
#     msg["From"] = EMAIL_ACCOUNT
#     msg["To"] = to
#
#     body = MIMEText(body, type, "utf-8")
#     msg.attach(body)
#     if os.path.exists(attachment):
#         with open(attachment,"rb") as f:
#             part = MIMEApplication(f.read(),Name = os.path.basename(attachment))
#         part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment)}"'
#         msg.attach(part)
#     with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
#         server.login(EMAIL_ACCOUNT, PASSWORD)
#         server.send_message(msg)
#     print("✅ 邮件已发送")

def record_new_employee_data(text):
    employee_blocks = re.split(r'\nName:', text)
    created = []
    for employee in employee_blocks:
        print("正在处理 ")


        if not employee.startswith('Name:'):
            employee = 'Name:' + employee + "\n"
        # print(employee)
        pattern = r"""
        Name:\s*(.+)\n+\s*
        Staff\ no:\s*(.+)\n+\s*
        Title:\s*(.+)\n+\s*
        Dept:\s*(.+)\n+\s*
        Direct\ Manager:\s*(.+?)\n+\s*
        On-board\ date:\s*(.+?)\n+\s*
        """
        matches = re.findall(pattern, employee, re.VERBOSE)
        print(matches)
        if matches:

            for m in matches:
                # data = {
                #     'name': m[0],
                #     'employee_id': m[1],
                #     'position': m[2],
                #     'department': m[3],
                #     'reporting_line': m[4],
                #     # 'onboard_date': "1998-05-05",
                #     'onboard_date': m[5],
                # }
                dept_name = m[3]
                dept_obj, _ = Department.objects.get_or_create(name=dept_name)
                data = {
                    'name': m[0].strip(),
                    'employee_id': m[1].strip(),
                    'mail': m[0].strip().replace(" ", ".") + "@iss-gf.com",
                    'position': m[2].strip(),
                    'department': dept_obj.id ,
                    'reporting_line': m[4].strip(),
                    # 'onboard_date': "1998-05-05",
                    'onboard_date': m[5].strip(),
                }

                serializer = EmployeeSerializer(data=data)

                if serializer.is_valid():
                    print("save success")
                    serializer.save()
                    created.append(serializer.data)

                else:
                    print(serializer.errors)
                    created.append(serializer.errors)
    return created