from rest_framework.generics import ListAPIView

from admin.serializers.sku_serializers import SKUSerializer
from goods.models import SKU
from admin.utils.pagination import MyPage


class SKUView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

    pagination_class = MyPage

    def get_queryset(self):
        # 获取keyword
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)

        return self.queryset.all()

