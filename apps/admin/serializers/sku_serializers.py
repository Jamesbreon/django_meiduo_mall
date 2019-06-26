from rest_framework import serializers

from goods.models import SKU, SKUSpecification, GoodsCategory, SPU, SPUSpecification, SpecificationOption


class SKUSpecificationSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()

    # 序列化specs字段
    specs = SKUSpecificationSerializer(many=True)

    class Meta:
        model = SKU
        fields = "__all__"

    # def create(self, validated_data):
    """
    {name: "1", spu_id: 1, caption: "3", category_id: 115, price: "4", cost_price: "4", market_price: "1",…}
    caption: "3"
    category_id: 115
    cost_price: "4"
    is_launched: ""
    market_price: "1"
    name: "1"
    price: "4"
    specs: [{spec_id: "2", option_id: 3}]
        0: {spec_id: "2", option_id: 3}
            option_id: 3
            spec_id: "2"
    spu_id: 1
    stock: "1"
    """

    def create(self, validated_data):
        # 获取前端传来的数据
        specs = validated_data.pop('specs')
        # 新建从表数据，主表中必须要有响应的sku
        sku = super().create(validated_data)
        # 保存中间表数据
        for temp in specs:
            temp['sku_id'] = sku.id
            SKUSpecification.objects.create(**temp)

        return sku

    def update(self, instance, validated_data):
        spec_option = validated_data.pop('specs')
        for temp in spec_option:
            option_model = SKUSpecification.objects.get(sku_id=instance.id, spec_id=temp['spec_id'])
            option_model.option_id = temp['option_id']
            option_model.save()
        # DRF提供的ModelSerializer 无法更新中间表
        return super().update(instance, validated_data)


class SKUCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ['id', 'name']


class SpecOptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecOptSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    # 与之关联的所有的从表对象
    options = SpecOptSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = ['id', 'options', 'spu_id', 'name', 'spu']
