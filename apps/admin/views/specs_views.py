from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from admin.serializers.specs_serializer import SpecSerializer
from admin.utils.pagination import MyPage


class SpecModelViewSet(ModelViewSet):
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSerializer
    pagination_class = MyPage