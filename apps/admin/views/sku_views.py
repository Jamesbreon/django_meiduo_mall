from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from admin.serializers.sku_serializers import SKUSerializer, SKUCategorySerializer, SPUSerializer, SPUSpecOptSerializer
from goods.models import SKU, GoodsCategory, SPU, SPUSpecification
from admin.utils.pagination import MyPage


# class SKUView(ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView):
class SKUView(ModelViewSet):
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


class GoodsSpecsView(ListAPIView):
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecOptSerializer

    def get_queryset(self):
        # 获取pk参数
        pk = self.kwargs.get('pk')
        if pk:
            return self.queryset.filter(pk=pk)
        return self.queryset.all()
