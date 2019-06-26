from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['name', 'default_image']


class OrderGoodsModelSerializer(serializers.ModelSerializer):
    sku = SKUModelSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku']


class OrdersModelSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    skus = OrderGoodsModelSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"


