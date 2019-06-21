from rest_framework import serializers

from goods.models import SPU, Brand, GoodsCategory


class SPUModelSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        # fields = "__all__"
        # 设置exclude因为新增数据进行反序列化时，前端以id的形式传入，无需对下列字段进行数据校验
        exclude = ['category1', 'category2', 'category3']


class BrandModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


class SKUCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']
