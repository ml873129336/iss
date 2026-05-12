import pandas as pd
from rest_framework.response import Response
from rest_framework import status
import platform
import subprocess
import os
from pdf2image import convert_from_path
from io import BytesIO
import base64
import tempfile

def excel_bytes_to_image_base64(excel_bytes):
    with tempfile.TemporaryDirectory() as tmpdir:
        excel_path = os.path.join(tmpdir, "file.xlsx")

        # 写文件
        with open(excel_path, "wb") as f:
            f.write(excel_bytes.getvalue())
        print("Excel写入完成:", os.path.exists(excel_path), os.path.getsize(excel_path))
        # Excel → PDF
        pdf_path = excel_to_pdf(excel_path, tmpdir)

        # PDF → 图片
        return pdf_to_image_base64(pdf_path)

def pdf_to_image_base64(pdf_path, dpi=200):
    try:
        # 1️⃣ 转换 PDF → 图片
        images = convert_from_path(pdf_path, dpi=dpi,
    poppler_path=r"D:\bin\poppler-25.12.0\Library\bin")

        print(f"[OK] PDF页数: {len(images)}")

        if not images:
            raise Exception("PDF没有任何页面")

        # 2️⃣ 取最后一页
        img = images[-1]

        # 3️⃣ 检查图片是否为空
        if img is None:
            raise Exception("图片对象为空")

        print(f"[OK] 图片尺寸: {img.size}, 模式: {img.mode}")

        # 4️⃣ 保存到内存
        buffer = BytesIO()
        img.save(buffer, format="PNG")

        img_bytes = buffer.getvalue()

        print(f"[OK] 图片字节大小: {len(img_bytes)}")

        if len(img_bytes) < 1000:
            raise Exception("图片数据异常（可能是空白页）")

        # 5️⃣ 转 base64
        base64_str = base64.b64encode(img_bytes).decode()

        print(f"[OK] base64长度: {len(base64_str)}")

        return base64_str

    except Exception as e:
        print("[ERROR] PDF转图片失败:", str(e))
        return None

def get_soffice_path():
    if platform.system() == "Windows":
        return r"C:\Program Files\LibreOffice\program\soffice.exe"
    return "soffice"


def excel_to_pdf(excel_path, output_dir):
    soffice = get_soffice_path()

    result = subprocess.run([
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        excel_path
    ], capture_output=True, text=True)

    print("LibreOffice stdout:", result.stdout)
    print("LibreOffice stderr:", result.stderr)

    if result.returncode != 0:
        raise Exception("LibreOffice转换失败")

    pdf_path = os.path.join(
        output_dir,
        os.path.basename(excel_path).replace(".xlsx", ".pdf")
    )

    #调试
    import shutil
    debug_path = r"D:\debug_output.pdf"
    shutil.copy(pdf_path, debug_path)

    print("已保存调试PDF:", debug_path)

    print("PDF是否存在:", os.path.exists(pdf_path))

    return pdf_path

def read_excel_to_df(uploaded_file, required_cols=None):
    """
    通用Excel读取方法
    ----------
    uploaded_file : Django UploadedFile 对象
    required_cols : list[str] 需要校验的列名，可选

    返回：
        成功 -> DataFrame
        失败 -> Response (包含错误信息)
    """
    if not uploaded_file:
        return Response({"error": "未上传Excel文件"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 读取Excel
        df = pd.read_excel(uploaded_file)

        # 校验必需列
        if required_cols:
            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                return Response({"error": f"缺少必要列：{', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        return df

    except Exception as e:
        return Response({"error": f"Excel读取失败：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


