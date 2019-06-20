from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView

from admin.serializers.sku_serializers import SKUSerializer, SKUCategorySerializer, SPUSerializer
from goods.models import SKU, GoodsCategory, SPU
from admin.utils.pagination import MyPage


class SKUView(ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

    pagination_class = MyPage

    def get_queryset(self):
        # 获取keyword
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(name__contains=keyword)

        return self.queryset.all()


# 新增商品获取三级分类及所属SPU
class SKUCategoryView(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = SKUCategorySerializer


# 获取SPU
class SPUView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSerializer

