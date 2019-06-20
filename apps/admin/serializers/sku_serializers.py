from rest_framework import serializers

from goods.models import SKU, SKUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    # 序列化specs字段
    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = "__all__"
