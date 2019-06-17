from django.shortcuts import render
import time, os
from django.conf import settings

from contents.models import ContentCategory
from .utils import get_categories


def generate_static_index_html():
    print('%s: generate_static_index_html' % time.ctime())

    contents = {}
    content_category_qs = ContentCategory.objects.all()
    for con in content_category_qs:
        contents[con.key] = con.content_set.filter(status=True).order_by('sequence')

    context = {
        'categories': get_categories(),
        'contents': contents
    }

    response = render(None, 'index.html', context)
    text_html = response.content.decode()
    # 静态文件路径
    path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(text_html)
