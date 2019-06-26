from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.response import Response

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from admin.serializers.channel_serializer import GoodsChannelSerializer, ChannelGroupSerializer, GoodsCategoryOneSerializer
from admin.utils.pagination import MyPage


class GoodsChannelModelViewSet(ModelViewSet):
    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelSerializer
    pagination_class = MyPage


    # 第二种展示增加弹框：频道方式
    @action(methods=['get'], detail=False)
    def channel_type(self, request):
        group_queyset = GoodsChannelGroup.objects.all()
        serializer = ChannelGroupSerializer(group_queyset, many=True)
        return Response(serializer.data)


    # 获取所以的一级分类
    @action(methods=['get'], detail=False)
    def categories(self, request):
        category_queryset = GoodsCategory.objects.filter(parent=None)
        serializer = GoodsCategoryOneSerializer(category_queryset, many=True)

        return Response(serializer.data)


# class ChannelGroupModelView(ListAPIView):
#     queryset = GoodsChannelGroup.objects.all()
#     serializer_class = ChannelGroupSerializer


# class GoodsCategoryOneModelView(ListAPIView):
#     queryset = GoodsCategory.objects.filter(parent=None)
#     serializer_class = GoodsCategoryOneSerializer
