from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView

from goods.models import SpecificationOption, SPUSpecification
from admin.serializers.option_serializer import OptionModelSerializer
from admin.serializers.specs_serializer import SpecSerializer
from admin.utils.pagination import MyPage


class OptionModelViewSet(ModelViewSet):
    queryset = SpecificationOption.objects.all()
    serializer_class = OptionModelSerializer
    pagination_class = MyPage


class OptionSimpleView(ListAPIView):
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSerializer
