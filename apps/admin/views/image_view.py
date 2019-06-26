from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response

from goods.models import SKUImage, SKU
from admin.serializers.image_serializer import SKUImageSerializer, SKUSimpleSerializer
from admin.utils.pagination import MyPage


class ImageView(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageSerializer
    pagination_class = MyPage


# skus/simple/
# Get
    @action(methods=['get'], detail=False)
    def simple(self, request):
        sku_querset = SKU.objects.all()
        serializer = SKUSimpleSerializer(sku_querset, many=True)
        return Response(serializer.data)
