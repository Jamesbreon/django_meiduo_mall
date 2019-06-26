from rest_framework.viewsets import ModelViewSet
# from rest_framework.generics import ListAPIView, RetrieveAPIView

from orders.models import OrderInfo
from admin.serializers.orders_serializer import OrdersModelSerializer  #OrdersDetailSerializer
from admin.utils.pagination import MyPage


class OrderInfoModelView(ModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrdersModelSerializer
    pagination_class = MyPage

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return self.queryset.filter(order_id__contains=keyword)

        return self.queryset.all()


# class OrderDetailModelView(RetrieveAPIView):
#     queryset = OrderInfo.objects.all()
#     serializer_class = OrdersDetailSerializer
