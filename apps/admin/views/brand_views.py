from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from admin.serializers.brand_serializer import BrandModelSerializer
from admin.utils.pagination import MyPage


class BrandModelView(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer
    pagination_class = MyPage
