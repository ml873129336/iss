
import os

from django.conf import settings
from django.http import FileResponse, Http404

def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(file_path):
        raise Http404("文件不存在")

    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response