from django.shortcuts import render
from django.views import View

from .models import ContentCategory
from .utils import get_categories


# Create your views here.
# 注册完成后的重定向到首页，这是广告内容视图函数
class IndexView(View):

    def get(self, request):

        contents = {}

        content_category_qs = ContentCategory.objects.all()
        for con in content_category_qs:
            contents[con.key] = con.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': get_categories(),
            'contents': contents
        }

        return render(request, 'index.html', context)
