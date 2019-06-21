from rest_framework.generics import ListAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, Brand, GoodsCategory
from admin.serializers.spu_serializer import SPUModelSerializer, BrandModelSerializer, SKUCategorySerializer
from admin.utils.pagination import MyPage


class SPUViewSet(ModelViewSet):
    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer

    pagination_class = MyPage


class SPUBrandView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer


class ChannelCategoryView(ListAPIView):
    queryset = GoodsCategory.objects.all()
    serializer_class = SKUCategorySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        if pk:
            return self.queryset.filter(parent_id=pk)

        return self.queryset.filter(parent=None)
